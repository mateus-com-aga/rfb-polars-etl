import polars as pl
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
RAW_DATA_DIR_EMP = BASE_DIR / "data" / "raw" / "emp"
RAW_DATA_GLOBS_EMP = (
    RAW_DATA_DIR_EMP / "*.csv",
    RAW_DATA_DIR_EMP / "*.EMPRECSV",
)
SILVER_DATA_PATH_EMP = BASE_DIR / "data" / "silver" / "empresas_consolidado.parquet"

EMPRESAS_SCHEMA = {
    "cnpj_basico": pl.String,
    "razao_social": pl.String,
    "natureza_juridica": pl.String,
    "qualificacao_responsavel": pl.String,
    "capital_social": pl.String,
    "porte_empresa": pl.String,
    "ente_federativo_responsavel": pl.String,
}
