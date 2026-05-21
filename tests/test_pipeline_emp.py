import pytest
import polars as pl
from pathlib import Path
from rfb_polars_etl.pipe_emp.pipeline_emp import extract_empresas

@pytest.fixture
def setup_dirs(tmp_path: Path):
    """Cria diretórios temporários para isolar os testes de I/O."""
    raw_dir = tmp_path / "raw"
    silver_dir = tmp_path / "silver"
    raw_dir.mkdir()
    silver_dir.mkdir()
    return raw_dir, silver_dir

def create_mock_emp_csv(path: Path, rows: list[str]):
    """Auxiliar para criar arquivos .EMPRECSV mockados com o layout de 7 colunas."""
    content = "\n".join(rows) + "\n"
    path.write_text(content, encoding="utf-8")

def test_extract_empresas_success(setup_dirs):
    """Verifica o processamento bem-sucedido, incluindo a conversão do capital social."""
    raw_dir, silver_dir = setup_dirs
    input_file = raw_dir / "D0123.EMPRECSV"
    output_file = silver_dir / "output.parquet"
    
    # Layout: cnpj_basico;razao_social;natureza_juridica;qualificacao_responsavel;capital_social;porte_empresa;ente_federativo_responsavel
    row = '12345678;RAZAO SOCIAL TESTE LTDA;2062;05;10500,50;01;BRASILIA'
    create_mock_emp_csv(input_file, [row])
    
    extract_empresas(str(raw_dir / "*.EMPRECSV"), str(output_file))
    
    df = pl.read_parquet(output_file)
    
    assert len(df) == 1
    assert df["cnpj_basico"].item() == "12345678"
    assert df["razao_social"].item() == "RAZAO SOCIAL TESTE LTDA"
    assert df["natureza_juridica"].dtype == pl.Int16
    assert df["capital_social"].item() == 10500.5  # Verifica conversão de vírgula para ponto e Float64
    assert df["porte_empresa"].item() == 1

def test_extract_empresas_null_handling(setup_dirs):
    """Garante que o pipeline não quebre com campos opcionais vazios."""
    raw_dir, silver_dir = setup_dirs
    input_file = raw_dir / "NULL_DATA.EMPRECSV"
    output_file = silver_dir / "output.parquet"
    
    # Simula campos vazios (separadores consecutivos)
    row = '87654321;EMPRESA SEM DADOS;;;;;'
    create_mock_emp_csv(input_file, [row])
    
    extract_empresas(str(raw_dir / "*.EMPRECSV"), str(output_file))
    
    df = pl.read_parquet(output_file)
    
    assert df["natureza_juridica"].item() is None
    assert df["capital_social"].item() is None
    assert df["porte_empresa"].item() is None

def test_extract_empresas_multiple_files(setup_dirs):
    """Testa a consolidação de múltiplos arquivos EMPRECSV em um único Parquet."""
    raw_dir, silver_dir = setup_dirs
    output_file = silver_dir / "consolidado.parquet"
    
    row1 = '11111111;EMPRESA 1;2062;05;1000,00;01;'
    row2 = '22222222;EMPRESA 2;2062;05;2000,00;03;'
    
    create_mock_emp_csv(raw_dir / "PARTE1.EMPRECSV", [row1])
    create_mock_emp_csv(raw_dir / "PARTE2.EMPRECSV", [row2])
    
    extract_empresas(str(raw_dir / "*.EMPRECSV"), str(output_file))
    
    df = pl.read_parquet(output_file)
    assert len(df) == 2
    assert set(df["cnpj_basico"].to_list()) == {"11111111", "22222222"}