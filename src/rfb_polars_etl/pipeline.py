import polars as pl
from collections.abc import Sequence
from pathlib import Path

from rfb_polars_etl.config import ESTABELECIMENTOS_SCHEMA

def extract_estabelecimentos(
    input_glob: Path | str | Sequence[Path | str],
    output_path: Path | str,
) -> None:
    """
    Executa a etapa de extração do pipeline, lendo arquivos .csv e .ESTABELE
    em streaming e consolidando-os em um único arquivo Parquet.
    """

    if isinstance(input_glob, (str, Path)):
        sources: str | list[str] = str(input_glob)
    else:
        sources = [str(pattern) for pattern in input_glob]

    # 1. Fase de Extração (I/O Bound)
    lf = pl.scan_csv(
        sources,
        separator=";",
        has_header=False,
        encoding="utf8-lossy",
        schema=ESTABELECIMENTOS_SCHEMA,
        infer_schema_length=0,
        low_memory=True, #Ativa o modo de baixo uso de memória, útil para arquivos grandes, mas pode reduzir a velocidade de leitura. Use com cautela.
        rechunk=True #Maelhorar performance de leitura, mas pode aumentar o uso de memória. Use com cautela.
    )

    # 2. Fase de Transformação (CPU Bound)
    lf_transformado = lf.with_columns([
        # Criando a coluna cnpj_completo concatenando as partes do CNPJ para cheve primária
        (pl.col("cnpj_basico") + pl.col("cnpj_ordem") + pl.col("cnpj_dv")).alias("cnpj_completo"),

        # Criando a coluna CEP_NUM para concatenar o CEP com o número do logradouro conforme exemplo: CEP-NUMERO.
        (pl.col("cep") + "-" + pl.col("numero")).alias("cep_numero"),

        # Convertendo as colunas de data para o formato Date do Polars
        pl.col("data_situacao_cadastral").str.to_date("%Y%m%d", strict=False),
        pl.col("data_inicio_atividade").str.to_date("%Y%m%d", strict=False),

        # Convertendo as colunas numéricas para tipos mais adequados
        pl.col("identificador_matriz_filial").cast(pl.Int8, strict=False),
        pl.col("situacao_cadastral").cast(pl.Int8, strict=False),
        pl.col("motivo_situacao_cadastral").cast(pl.Int16, strict=False),
    ])

    # 3. Fase de Carga (I/O Bound)
    lf_transformado.sink_parquet(
        str(output_path),
        compression="zstd",
        compression_level=3, #Nível de compressão zstd, onde 1 é o mais rápido e 22 é o mais comprimido. O nível 3 é um bom equilíbrio entre I/O x CPU.
        row_group_size=100_000, #Viabiliza o skipping eficiente durante a leitura.
        statistics=True, #Gera estatísticas para cada coluna, o que melhora o desempenho de leitura e filtragem.
    )