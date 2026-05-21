import polars as pl
from rfb_polars_etl.pipe_stab.config_estab import SILVER_DATA_PATH
from rfb_polars_etl.pipe_emp.config_emp import SILVER_DATA_PATH_EMP
from pathlib import Path
from rfb_polars_etl.grupos_cidades.pipeline_grupos import extract_cep_num

def query_estabelecimentos():
    # Usando o caminho absoluto definido centralizadamente no config.py
    parquet_path = SILVER_DATA_PATH
    gold_path = Path(__file__).resolve().parent.parent.parent / "data" / "gold"

    if not parquet_path.exists():
        print(f"Erro: O arquivo {parquet_path} não existe. Rode o pipeline primeiro.")
        return

    # Traduzir o código do município para o nome correspondente (opcional, mas melhora a legibilidade)
    codigo_para_nome_municipio = {
        "8589": 'CANOAS',
        "8845": 'SANTANA DO LIVRAMENTO',
        "8927": 'TAQUARA',
        "8953": 'VACARIA',
        "8559": 'CACHOEIRA DO SUL',
        "8651": 'ESTEIO'
    }
    # Lista de municípios solicitada (mantidos como string para match com o schema)
    municipios_alvo = list(codigo_para_nome_municipio.keys())

    # Colunas desejadas
    colunas = [
        "cnpj_basico", "cnpj_completo", "situacao_cadastral", 
        "logradouro", "numero", "bairro", "uf",
        "municipio", "cep", "cep_numero",
        "ddd_1", "telefone_1"
    ]

    # Execução Lazy: O Polars só lerá as colunas solicitadas e as linhas que passarem no filtro de municipio e de situação cadastral
    df_estab = (
        pl.scan_parquet(parquet_path)
        .filter((pl.col("municipio").is_in(municipios_alvo)) 
                & (pl.col("situacao_cadastral") == 2) 
                & (pl.col("ddd_1").str.starts_with("5")))
        .select(colunas)
    )

    df_estab = df_estab.with_columns(
        pl.col("municipio")
        .cast(pl.Utf8)
        .replace(codigo_para_nome_municipio)
    )

    # Se o "telefone_1" começar com algo que nao seja 3, ele deve ser formatado com o 9 na frente.
    df_estab = df_estab.with_columns(
        pl.when(pl.col("telefone_1").str.starts_with("3").not_())
        .then(pl.col("ddd_1") + pl.lit("9") + pl.col("telefone_1"))
        .otherwise(pl.col("ddd_1") + pl.col("telefone_1"))
        .alias("telefone_1")
    )

    # Coluna CEP-NUMERO dos grupos de cidades para join
    cep_numero = extract_cep_num().lazy()
    
    # Join com .parquet data/silver/empresas_consolidado.parquet para trazer a razão social usando duckdb
    df_emp = (
        pl.scan_parquet(SILVER_DATA_PATH_EMP)
        .select(["cnpj_basico", "razao_social"])
    )

    df_concat = (
        df_estab
        .join(df_emp, on="cnpj_basico", how="left")
        # .collect(engine="streaming")
    )

    df_final = (
        df_concat
        .join(cep_numero, on="cep_numero", how="inner")
        .collect(engine="streaming")
    )

    # Exibe o resultado e salva um CSV para conferência
    print(f"Empresas encontradas: {df_final.height}")
    print(df_final.head(df_final.height))

    # Opcional: exportar para CSV na pasta gold.
    df_final.write_csv(gold_path / "empresas_municipios_selecionados.csv")

    # df_final.write_excel(gold_path / "empresas_municipios_selecionados.xlsx")

    print("Consulta concluída. Arquivo 'empresas_municipios_selecionados.csv' salvo com os resultados.")

    return df_final

if __name__ == "__main__":
    query_estabelecimentos()