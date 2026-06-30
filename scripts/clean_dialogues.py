"""
Pipeline de nettoyage et de préparation des données pour fine-tuning LoRA.

Étapes :
  1. Élimination des doublons (exacts + quasi-doublons sur Patient+Doctor)
  2. Éradication des données compromises (anti-sabotage / prompt injection)
  3. Anonymisation des PII (emails, numéros de téléphone)
  4. Normalisation textuelle (flèches, tirets décoratifs, espaces)
  5. Filtrage de la qualité conversationnelle (longueur input/output)
  6. Séparation stratégique train (85%) / eval (15%) via une colonne 'split'
  7. Formatage LoRA (renommage des colonnes -> instruction / input / output)

Entrée  : dialogues.parquet (colonnes Description, Patient, Doctor)
Sortie  : dialogues_final.csv (toutes les lignes, avec une colonne 'split'
          valant 'train' ou 'eval')
"""

import re
import duckdb
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

parquet_path = Path("datasets/dialogues.parquet")
output_final = Path("datasets/dialogues_final.csv")

# le seed est fixé pour garantir la reproductibilité de la séparation train/eval
# le ratio train/eval est fixé à 85% / 15% pour maximiser la quantité de données d'entraînement
# les bornes de longueur des inputs/outputs sont fixées pour garantir une qualité minimale des dialogues

RANDOM_SEED = 42
TRAIN_RATIO = 0.85

MIN_WORDS_INPUT = 10
MAX_WORDS_INPUT = 500
MIN_WORDS_OUTPUT = 10
MAX_WORDS_OUTPUT = 500

# Patterns de prompt injection / sabotage. Volontairement stricts (ancrés sur
# des tournures de phrase complètes) pour éviter les faux positifs sur du
# vocabulaire médical légitime (ex. "disregard my GP", "disregard for laws").
SABOTAGE_PATTERNS = [
    r"ignore (all|any|the)?\s*(previous|prior|above)\s+instructions",
    r"disregard (all|any|the)?\s*(previous|prior|above)\s+instructions",
    r"as an ai (language model|assistant)\b",
    r"\byou are now\b.{0,30}\b(chatgpt|gpt|dan|jailbreak)\b",
    r"\bjailbreak\b",
    r"\bsystem prompt\b",
    r"\bact as (a|an)?\s*(dan|jailbroken|unrestricted)\b",
    r"\boverride (your|the) instructions\b",
    r"\bpretend (you are|to be) (an? )?ai\b",
    r"\bdo anything now\b",
]
SABOTAGE_REGEX = re.compile("|".join(SABOTAGE_PATTERNS), flags=re.IGNORECASE)

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(
    r"(?<!\d)(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?){2,4}\d{3,4}(?!\d)"
)

ARROW_REGEX = re.compile(r"-{2,3}>\s*")
DASH_REGEX = re.compile(r"-{4,}")
SPACE_REGEX = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# 1. Chargement
# ---------------------------------------------------------------------------

# Vérification de l'existence du fichier parquet

if not parquet_path.exists():
    raise FileNotFoundError(f"Le fichier {parquet_path} est introuvable.")

# sélection des colonnes pertinentes et élimination des lignes vides

print(f"Chargement de {parquet_path}...")
df = duckdb.sql(f"""
    SELECT
        TRIM(Description) AS Description,
        TRIM(Patient) AS Patient,
        TRIM(Doctor) AS Doctor
    FROM '{parquet_path.as_posix()}'
    WHERE Description IS NOT NULL AND TRIM(Description) <> ''
      AND Patient IS NOT NULL AND TRIM(Patient) <> ''
      AND Doctor IS NOT NULL AND TRIM(Doctor) <> ''
""").df()
print(f"  -> {len(df)} lignes chargées")


# ---------------------------------------------------------------------------
# 2. Élimination des doublons
# ---------------------------------------------------------------------------

before = len(df)
df = df.drop_duplicates(subset=["Description", "Patient", "Doctor"])
df = df.drop_duplicates(subset=["Patient", "Doctor"])  # quasi-doublons
print(f"Doublons supprimés : {before - len(df)} (reste {len(df)})")


# ---------------------------------------------------------------------------
# 3. Éradication des données compromises (anti-sabotage)
# ---------------------------------------------------------------------------

# On supprime les lignes contenant des patterns de prompt injection / sabotage

before = len(df)
mask_sabotage = (
    df["Description"].str.contains(SABOTAGE_REGEX, na=False)
    | df["Patient"].str.contains(SABOTAGE_REGEX, na=False)
    | df["Doctor"].str.contains(SABOTAGE_REGEX, na=False)
)
df = df[~mask_sabotage]
print(f"Lignes compromises (prompt injection) supprimées : {before - len(df)} (reste {len(df)})")


# ---------------------------------------------------------------------------
# 4. Anonymisation des PII (personally identifiable information : emails, numéros de téléphone)
# ---------------------------------------------------------------------------

# On remplace les emails et numéros de téléphone par des tokens [EMAIL] et [PHONE]

def anonymize(text: str) -> str:
    text = EMAIL_REGEX.sub("[EMAIL]", text)
    text = PHONE_REGEX.sub("[PHONE]", text)
    return text

for col in ["Description", "Patient", "Doctor"]:
    df[col] = df[col].apply(anonymize)
print("Anonymisation des emails et numéros de téléphone effectuée.")


# ---------------------------------------------------------------------------
# 5. Normalisation textuelle (flèches, tirets décoratifs, espaces)
# ---------------------------------------------------------------------------

# On remplace les flèches et tirets décoratifs par des espaces, et on normalise les espaces multiples

def normalize(text: str) -> str:
    text = ARROW_REGEX.sub(" ", text)   # --> / --->
    text = DASH_REGEX.sub(" ", text)    # ----  (4 tirets ou plus)
    text = SPACE_REGEX.sub(" ", text).strip()
    return text

for col in ["Description", "Patient", "Doctor"]:
    df[col] = df[col].apply(normalize)
print("Normalisation textuelle effectuée.")


# ---------------------------------------------------------------------------
# 6. Filtrage de la qualité conversationnelle (longueur input/output)
# ---------------------------------------------------------------------------

# On filtre les dialogues dont la longueur (en nombre de mots) de l'input ou de l'output est hors bornes

before = len(df)
input_word_count = df["Patient"].str.split().str.len()
output_word_count = df["Doctor"].str.split().str.len()

mask_quality = (
    input_word_count.between(MIN_WORDS_INPUT, MAX_WORDS_INPUT)
    & output_word_count.between(MIN_WORDS_OUTPUT, MAX_WORDS_OUTPUT)
)
df = df[mask_quality]
print(f"Lignes filtrées (longueur input/output hors bornes) : {before - len(df)} (reste {len(df)})")


# ---------------------------------------------------------------------------
# 7. Reformatage final (suppression doublons résiduels post-nettoyage)
# ---------------------------------------------------------------------------

# On supprime les doublons résiduels sur Patient+Doctor après normalisation, pour éviter d'avoir plusieurs dialogues identiques entre le même patient et le même médecin

before = len(df)
df = df.drop_duplicates(subset=["Patient", "Doctor"])
print(f"Doublons résiduels post-normalisation supprimés : {before - len(df)} (reste {len(df)})")


# ---------------------------------------------------------------------------
# 8. Renommage des colonnes pour le format LoRA (Alpaca-style)
# ---------------------------------------------------------------------------

# On renomme les colonnes pour correspondre au format attendu par LoRA (Alpaca-style) : "Description" -> "instruction", "Patient" -> "input", "Doctor" -> "output"

df = df.rename(columns={
    "Description": "instruction",
    "Patient": "input",
    "Doctor": "output",
})


# ---------------------------------------------------------------------------
# 9. Séparation stratégique (train 85% / eval 15%)
# ---------------------------------------------------------------------------

# On mélange les lignes de manière aléatoire (seed fixe pour reproductibilité) et on sépare en deux ensembles : train (85%) et eval (15%), en ajoutant une colonne 'split' indiquant le type d'ensemble

df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
split_idx = int(len(df) * TRAIN_RATIO)
df["split"] = "eval"
df.loc[:split_idx - 1, "split"] = "train"

df.to_csv(output_final, index=False)

n_train = (df["split"] == "train").sum()
n_eval = (df["split"] == "eval").sum()
print(f"\nExport terminé :")
print(f"  - {output_final} : {len(df)} lignes au total")
print(f"      dont train : {n_train} ({TRAIN_RATIO*100:.0f}%)")
print(f"      dont eval  : {n_eval} ({(1-TRAIN_RATIO)*100:.0f}%)")