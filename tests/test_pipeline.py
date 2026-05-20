import pytest
import polars as pl
from pathlib import Path
from rfb_polars_etl.pipe_stab.pipeline_estab import extract_estabelecimentos

# Fixture para isolar o ambiente de I/O de cada teste
@pytest.fixture
def setup_dirs(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    silver_dir = tmp_path / "silver"
    raw_dir.mkdir()
    silver_dir.mkdir()
    return raw_dir, silver_dir

def create_mock_csv(path: Path, rows: list[str]):
    """Auxiliar para criar arquivos .ESTABELE mockados com 30 colunas"""
    # A string deve conter exatamente 29 pontos e vírgula para representar 30 colunas
    content = "\n".join(rows) + "\n"
    path.write_text(content, encoding="latin1")

# --- TESTE 1: CAMINHO FELIZ (HAPPY PATH) ---
def test_extract_success(setup_dirs):
    raw_dir, silver_dir = setup_dirs
    input_file = raw_dir / "D0123.ESTABELE"
    output_file = silver_dir / "output.parquet"
    
    # Linha padrão com 30 colunas
    row = '12345678;0001;99;1;EMPRESA TESTE;2;20240101;00;;;20230101;1234;SEC;RUA;AV;10;C;BAIRRO;90000;RS;8888;51;9999;51;8888;51;7777;mail@test.com;;'
    create_mock_csv(input_file, [row])
    
    extract_estabelecimentos(str(raw_dir / "*.ESTABELE"), str(output_file))
    
    df = pl.read_parquet(output_file)
    
    assert len(df) == 1
    assert df["cnpj_completo"].item() == "12345678000199"
    assert df["situacao_cadastral"].dtype == pl.Int8
    assert df["situacao_cadastral"].item() == 2

# --- TESTE 2: TRATAMENTO DE VALORES NULOS ---
def test_extract_with_nulls(setup_dirs):
    raw_dir, silver_dir = setup_dirs
    input_file = raw_dir / "NULL_DATA.ESTABELE"
    output_file = silver_dir / "output.parquet"
    
    # Simula campos críticos vazios (;;;)
    row = '87654321;0002;11;2;;;;;;;;;;;;;;;;;;;;;;;;;' # Preenchido com o mínimo de separadores
    # Garante que temos as 30 colunas mesmo vazias
    row_full = row + ";" * (29 - row.count(";")) 
    
    create_mock_csv(input_file, [row_full])
    
    extract_estabelecimentos(str(raw_dir / "*.ESTABELE"), str(output_file))
    
    df = pl.read_parquet(output_file)
    
    # O casting de situacao_cadastral (vazio) para Int8 deve resultar em Null, não em erro
    assert df["situacao_cadastral"].item() is None
    assert df["cnpj_completo"].item() == "87654321000211"
    assert df["nome_fantasia"].item() is None

# --- TESTE 3: RESILIÊNCIA A ARQUIVO VAZIO ---
def test_extract_empty_file(setup_dirs):
    raw_dir, silver_dir = setup_dirs
    input_file = raw_dir / "EMPTY.ESTABELE"
    output_file = silver_dir / "output.parquet"
    
    input_file.write_text("", encoding="latin1") # Arquivo existe, mas sem conteúdo
    
    # O Polars deve lidar com isso ou gerar um log de erro, mas não travar o processo
    # Dependendo da implementação, ele gera um Parquet vazio com o Schema correto
    extract_estabelecimentos(str(raw_dir / "*.ESTABELE"), str(output_file))
    
    if output_file.exists():
        df = pl.read_parquet(output_file)
        assert len(df) == 0

# --- TESTE 4: MULTIPLOS ARQUIVOS (CONSOLIDAÇÃO) ---
def test_extract_multiple_files(setup_dirs):
    raw_dir, silver_dir = setup_dirs
    output_file = silver_dir / "consolidated.parquet"
    
    row1 = '11111111;0001;11;1;FILIAL 1' + ';' * 25
    row2 = '22222222;0001;22;1;FILIAL 2' + ';' * 25
    
    create_mock_csv(raw_dir / "PART1.ESTABELE", [row1])
    create_mock_csv(raw_dir / "PART2.ESTABELE", [row2])
    
    extract_estabelecimentos(str(raw_dir / "*.ESTABELE"), str(output_file))
    
    df = pl.read_parquet(output_file)
    assert len(df) == 2
    assert set(df["cnpj_basico"].to_list()) == {"11111111", "22222222"}