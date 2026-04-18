import polars as pl
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "*.ESTABELE"
SILVER_DATA_PATH = BASE_DIR / "data" / "silver" / "estabelecimentos_consolidado.parquet"

ESTABELECIMENTOS_SCHEMA = {
    "cnpj_basico": pl.String,
    "cnpj_ordem": pl.String,
    "cnpj_dv": pl.String,
    "identificador_matriz_filial": pl.String,
    "nome_fantasia": pl.String,
    "situacao_cadastral": pl.String,
    "data_situacao_cadastral": pl.String,
    "motivo_situacao_cadastral": pl.String,
    "nome_cidade_exterior": pl.String,
    "pais": pl.String,
    "data_inicio_atividade": pl.String,
    "cnae_principal": pl.String,
    "cnae_secundario": pl.String,
    "tipo_logradouro": pl.String,
    "logradouro": pl.String,
    "numero": pl.String,
    "complemento": pl.String,
    "bairro": pl.String,
    "cep": pl.String,
    "uf": pl.String,
    "municipio": pl.String,
    "ddd_1": pl.String,
    "telefone_1": pl.String,
    "ddd_2": pl.String,
    "telefone_2": pl.String,
    "ddd_fax": pl.String,
    "fax": pl.String,
    "correio_eletronico": pl.String,
    "situacao_especial": pl.String,
    "data_situacao_especial": pl.String,
}