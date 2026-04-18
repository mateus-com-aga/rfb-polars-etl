import time
from pathlib import Path
from rfb_polars_etl.config import RAW_DATA_PATH, SILVER_DATA_PATH
from rfb_polars_etl.pipeline import extract_estabelecimentos

def main() -> None:
    print(f"Analisando arquivos em: {RAW_DATA_PATH}")

    # Garante que o diretório 'silver' exista antes de tentar gravar
    Path(SILVER_DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()

    try:
        extract_estabelecimentos(RAW_DATA_PATH, SILVER_DATA_PATH)
        elapsed_time = time.time() - start_time
        print(f"Processamento concluído em {elapsed_time:.2f} segundos.")
        print(f"Arquivo consolidado salvo em: {SILVER_DATA_PATH}")
    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    main()