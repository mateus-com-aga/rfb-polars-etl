import polars as pl
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parent / "grupo_5.xlsx"

def extract_cep_num():
    if not FILE_PATH.exists():
        raise FileNotFoundError(f"Arquivo fonte não localizado: {FILE_PATH}")
    
    tabela_grupos = pl.read_excel(
        source=FILE_PATH,
        engine="calamine",
    )

    cep_numero = tabela_grupos.with_columns(
        (pl.col("CEP").cast(pl.Utf8) + "-" + pl.col("NUM").cast(pl.Utf8)).alias("cep_numero")
    ).select(["cep_numero"])

    return cep_numero

if __name__ == "__main__":
    extract_cep_num()