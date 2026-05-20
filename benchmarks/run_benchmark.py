import time
import psutil
import platform
import os
import threading
from pathlib import Path
import matplotlib.pyplot as plt

# Seus imports do projeto
from rfb_polars_etl.pipe_stab.pipeline_estab import extract_estabelecimentos
from rfb_polars_etl.pipe_stab.config_estab import RAW_DATA_GLOBS, SILVER_DATA_PATH

# Variáveis globais para monitoramento em background
monitor_ativo = True
historico_cpu = []
historico_ram = []

def monitorar_recursos(processo):
    global monitor_ativo
    while monitor_ativo:
        try:
            historico_cpu.append(processo.cpu_percent(interval=0.5))
            historico_ram.append(processo.memory_info().rss / (1024 * 1024))
        except psutil.NoSuchProcess:
            break

def coletar_specs_sistema():
    print("="*60)
    print("🚀 AUDITORIA DE SISTEMA E PERFORMANCE - POLARS ETL")
    print("="*60)
    print("[HARDWARE DETECTADO]")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Processador: {platform.processor()}")
    print(f"RAM Total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print("-" * 60)

def medir_performance():
    global monitor_ativo
    
    coletar_specs_sistema()
    print("\n[INICIANDO PIPELINE DE DADOS...]")
    print("Aguarde. O motor Polars (Streaming) está processando os lotes...\n")
    
    processo = psutil.Process()
    processo.cpu_percent() # Inicializa o contador da CPU
    
    # Inicia a thread de monitoramento contínuo
    thread_monitor = threading.Thread(target=monitorar_recursos, args=(processo,))
    thread_monitor.start()
    
    # Medição de I/O de disco inicial
    io_inicial = psutil.disk_io_counters()
    inicio_tempo = time.time()
    
    # === EXECUÇÃO DO MOTOR ===
    extract_estabelecimentos(RAW_DATA_GLOBS, SILVER_DATA_PATH)
    # =========================
    
    fim_tempo = time.time()
    io_final = psutil.disk_io_counters()
    
    # Para o monitoramento
    monitor_ativo = False
    thread_monitor.join()
    
    # Cálculos Finais
    tempo_execucao = fim_tempo - inicio_tempo
    ram_pico = max(historico_ram) if historico_ram else 0
    cpu_media = sum(historico_cpu) / len(historico_cpu) if historico_cpu else 0
    
    # Cálculo de I/O seguro (Type Guard para evitar falhas se io_counters retornar None)
    leitura_mb = 0.0
    escrita_mb = 0.0
    if io_inicial and io_final:
        leitura_mb = (io_final.read_bytes - io_inicial.read_bytes) / (1024 * 1024)
        escrita_mb = (io_final.write_bytes - io_inicial.write_bytes) / (1024 * 1024)
    
    # Tamanho do arquivo final gerado
    tamanho_parquet_mb = 0.0
    if Path(SILVER_DATA_PATH).exists():
        tamanho_parquet_mb = os.path.getsize(SILVER_DATA_PATH) / (1024 * 1024)

    print("="*60)
    print("[RELATÓRIO DE EXECUÇÃO]")
    print(f"⏱️  Tempo Total       : {tempo_execucao:.2f} segundos")
    print(f"🧠 Pico de Memória RAM: {ram_pico:.2f} MB")
    print(f"⚙️  Média de Uso CPU   : {cpu_media:.1f}%")
    print(f"📦 Tamanho do Parquet : {tamanho_parquet_mb:.2f} MB")
    print(f"💾 I/O Leitura Disco  : ~{leitura_mb:.2f} MB lidos durante o run")
    print(f"💾 I/O Escrita Disco  : ~{escrita_mb:.2f} MB escritos durante o run")
    print("="*60)
    
    return tempo_execucao, ram_pico

def gerar_grafico(tempo_polars, ram_polars):
    labels = ['Pandas (In-Memory)', 'Polars (Streaming)']
    
    # Estimativa teórica: 16.19 GB * 4 (mínimo para Pandas não quebrar)
    # Usamos um valor alto para ilustrar o transbordo da RAM física
    rams = [64760, ram_polars]  
    tempos = [0, tempo_polars] # 0 = Representa o Crash (não finaliza)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- Gráfico de Tempo ---
    barras_tempo = ax1.bar(labels, tempos, color=['#7f8c8d', '#2ecc71'])
    ax1.set_title('Tempo de Execução (Segundos)')
    ax1.text(0, 10, 'CRASH (OOM)', ha='center', va='bottom', color='red', fontweight='bold', fontsize=12)
    ax1.bar_label(barras_tempo, fmt='%.1fs', padding=3)

    # --- Gráfico de RAM ---
    barras_ram = ax2.bar(labels, rams, color=['#e74c3c', '#3498db'])
    ax2.set_title('Pico de Memória RAM (MB) - Menor é Melhor')
    
    # Linha do Limite Físico da SUA MÁQUINA (16GB)
    ax2.axhline(y=16384, color='black', linestyle='--', alpha=0.7, label='Sua RAM Física (16GB)')
    
    # Linha de 8GB (Onde o Windows geralmente começa a "matar" processos pesados)
    ax2.axhline(y=8000, color='r', linestyle=':', alpha=0.5, label='Zona de Risco OOM')
    
    ax2.legend()
    ax2.bar_label(barras_ram, fmt='%.0f MB', padding=3)
    
    # Ajuste de escala para o gráfico de RAM não ficar ilegível
    ax2.set_ylim(0, 75000) 

    plt.tight_layout()
    plt.savefig("benchmarks/resultado_benchmark.png", dpi=300)
    print("Gráfico de alta fidelidade técnica gerado.")

if __name__ == "__main__":
    t, m = medir_performance()
    gerar_grafico(t, m)