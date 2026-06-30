import duckdb
from pathlib import Path

parquet_path = Path("dialogues.parquet")
output_csv = Path("dialogues_clean.csv")

if not parquet_path.exists():
    raise FileNotFoundError(f"Le fichier {parquet_path} est introuvable.")

query = f"""
COPY (
    SELECT
        TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(Description, '-{{2,3}}>\\s*', ' ', 'g'), '-{{4,}}', ' ', 'g'), '\\s+', ' ', 'g')) AS Description,
        TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(Patient, '-{{2,3}}>\\s*', ' ', 'g'), '-{{4,}}', ' ', 'g'), '\\s+', ' ', 'g')) AS Patient,
        TRIM(REGEXP_REPLACE(REGEXP_REPLACE(REGEXP_REPLACE(Doctor, '-{{2,3}}>\\s*', ' ', 'g'), '-{{4,}}', ' ', 'g'), '\\s+', ' ', 'g')) AS Doctor
    FROM '{parquet_path.as_posix()}'
    WHERE Description IS NOT NULL AND TRIM(Description) <> ''
      AND Patient IS NOT NULL AND TRIM(Patient) <> ''
      AND Doctor IS NOT NULL AND TRIM(Doctor) <> ''
) TO '{output_csv.as_posix()}' (HEADER TRUE, DELIMITER ',')
"""

print(f"Nettoyage de {parquet_path} et export vers {output_csv}...")
duckdb.sql(query)
print("Export terminé.")