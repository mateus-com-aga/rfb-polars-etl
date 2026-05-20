import time
from pathlib import Path

from rfb_polars_etl.pipe_stab.config_estab import RAW_DATA_DIR, RAW_DATA_GLOBS, SILVER_DATA_PATH
from rfb_polars_etl.pipe_emp.config_emp import RAW_DATA_DIR_EMP, RAW_DATA_GLOBS_EMP, SILVER_DATA_PATH_EMP

from rfb_polars_etl.pipe_stab.pipeline_estab import extract_estabelecimentos
from rfb_polars_etl.pipe_emp.pipeline_emp import extract_empresas

def main() -> None:
    print(f"Analisando arquivos em: {RAW_DATA_DIR}")
    for pattern in RAW_DATA_GLOBS:
        print(f"  - {pattern}")

    print(f"Analisando arquivos em: {RAW_DATA_DIR_EMP}")
    for pattern in RAW_DATA_GLOBS_EMP:
        print(f"  - {pattern}")

    # Garante que o diretório 'silver' exista antes de tentar gravar
    Path(SILVER_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(SILVER_DATA_PATH_EMP).parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()

    try:
        extract_estabelecimentos(RAW_DATA_GLOBS, SILVER_DATA_PATH)
        print(f"Arquivo de estabelecimentos consolidado salvo em: {SILVER_DATA_PATH}")

        extract_empresas(RAW_DATA_GLOBS_EMP, SILVER_DATA_PATH_EMP)
        print(f"Arquivo de empresas consolidado salvo em: {SILVER_DATA_PATH_EMP}")

        elapsed_time = time.time() - start_time
        print(f"Processamento concluído em {elapsed_time:.2f} segundos.")
        
    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    main()