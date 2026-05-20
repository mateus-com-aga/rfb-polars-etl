import polars as pl
from collections.abc import Sequence
from pathlib import Path

from rfb_polars_etl.pipe_emp.config_emp import EMPRESAS_SCHEMA

def extract_empresas(
    input_glob: Path | str | Sequence[Path | str],
    output_path: Path | str,
) -> None:

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
        schema=EMPRESAS_SCHEMA,
        infer_schema_length=0,
        low_memory=True,
    )

    # 2. Fase de Transformação (CPU Bound)
    lf_transformado = lf.with_columns([
        pl.col("natureza_juridica").cast(pl.Int16, strict=False),
        pl.col("qualificacao_responsavel").cast(pl.Int8, strict=False),
        # Tratando capital_social: substitui vírgula por ponto para conversão numérica
        pl.col("capital_social").str.replace(",", ".").cast(pl.Float64, strict=False),
        pl.col("porte_empresa").cast(pl.Int8, strict=False),
    ])

    # 3. Fase de Carga (I/O Bound)
    lf_transformado.sink_parquet(
        str(output_path),
        compression="zstd",
        compression_level=3,
        row_group_size=100_000,
        statistics=True,
    )