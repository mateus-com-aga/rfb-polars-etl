import polars as pl
from rfb_polars_etl.config import SILVER_DATA_PATH

def query_estabelecimentos():
    # Usando o caminho absoluto definido centralizadamente no config.py
    parquet_path = SILVER_DATA_PATH

    if not parquet_path.exists():
        print(f"Erro: O arquivo {parquet_path} não existe. Rode o pipeline primeiro.")
        return

    # Lista de municípios solicitada (mantidos como string para match com o schema)
    municipios_alvo = ["8541", "8771", "8791", "8963", "8839", "8569"]

    # Colunas desejadas
    colunas = [
        "cnpj_completo", "situacao_cadastral", "nome_fantasia", 
        "logradouro", "numero", "bairro", "uf", "municipio", "cep", "ddd_1", "telefone_1"
    ]

    # Execução Lazy: O Polars só lerá as colunas solicitadas e as linhas que passarem no filtro de municipio e de situação cadastral
    df = (
        pl.scan_parquet(parquet_path)
        .filter((pl.col("municipio").is_in(municipios_alvo)) 
                & (pl.col("situacao_cadastral") == 2) 
                & (pl.col("ddd_1").str.starts_with("5")))
        .select(colunas)
        .collect(engine="streaming")
    )

    # Traduzir o código do município para o nome correspondente (opcional, mas melhora a legibilidade)
    codigo_para_nome_municipio = {
        "8771": 'NOVO HAMBURGO',
        "8569": 'CAMAQUA',
        "8541": 'BENTO GONCALVES',
        "8791": 'PELOTAS',
        "8963": 'VIAMAO',
        "8839": 'SANTA CRUZ DO SUL'
    }

    df = df.with_columns(
        pl.col("municipio")
        .cast(pl.Utf8)
        .replace(codigo_para_nome_municipio)
    )

    # Se o "telefone_1" começar com algo que nao seja 3, ele deve ser formatado com o 9 na frente.
    df = df.with_columns(
        pl.when(pl.col("telefone_1").str.starts_with("3").not_())
        .then(pl.lit("9") + pl.col("telefone_1"))
        .otherwise(pl.col("telefone_1"))
        .alias("telefone_1")
    )
    


    # Exibe o resultado e salva um CSV para conferência
    print(f"Empresas encontradas: {df.height}")
    print(df.head(10))

    # Opcional: exportar para CSV
    # df.write_csv("empresas_municipios_selecionados.csv")
    df.write_excel("empresas_municipios_selecionados.xlsx")

    print("Consulta concluída. Arquivo 'empresas_municipios_selecionados.xlsx' salvo com os resultados.")

    return df

if __name__ == "__main__":
    query_estabelecimentos()