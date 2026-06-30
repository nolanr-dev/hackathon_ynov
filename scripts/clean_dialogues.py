import duckdb
from pathlib import Path

parquet_path = Path("dialogues.parquet")
output_csv = Path("dialogues_clean.csv")

if not parquet_path.exists():
    raise FileNotFoundError(f"Le fichier {parquet_path} est introuvable.")

query = f"""
COPY (
    SELECT
        TRIM(Description) AS Description,
        TRIM(Patient) AS Patient,
        TRIM(Doctor) AS Doctor
    FROM '{parquet_path.as_posix()}'
    WHERE Description IS NOT NULL AND TRIM(Description) <> ''
      AND Patient IS NOT NULL AND TRIM(Patient) <> ''
      AND Doctor IS NOT NULL AND TRIM(Doctor) <> ''
) TO '{output_csv.as_posix()}' (HEADER TRUE, DELIMITER ',')
"""

print(f"Nettoyage de {parquet_path} et export vers {output_csv}...")
duckdb.sql(query)
print("Export terminé.")
