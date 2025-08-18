import requests
import threading
import os

# URL do webhook de teste do n8n (ajuste para produção se necessário)
N8N_WEBHOOK_URL = "https://zezim123.app.n8n.cloud/webhook-test/0f8dfe703-2b9c-49f0-9004-a27790505bae"

def n8n_send_event(event_type, data):
    payload = {"tipo": event_type, "dados": data}
    try:
        requests.post(N8N_WEBHOOK_URL, json=payload, timeout=3)
    except Exception:
        pass

def report_error_to_n8n(error_msg, context=None):
    n8n_send_event("erro", {"mensagem": str(error_msg), "contexto": context or {}})

def send_log_to_n8n(log_data):
    n8n_send_event("log", log_data)

def send_metrics_to_n8n(metrics):
    n8n_send_event("metricas", metrics)

def notify_file_to_n8n(filepath):
    if os.path.exists(filepath):
        n8n_send_event("upload", {"arquivo": filepath})

def send_download_queue_to_n8n(queue):
    n8n_send_event("fila_download", {"itens": queue})

# Exemplo de uso periódico para métricas/logs
def schedule_periodic_metrics(get_metrics_func, interval_sec=3600):
    def _send():
        try:
            send_metrics_to_n8n(get_metrics_func())
        except Exception:
            pass
        threading.Timer(interval_sec, _send).start()
    _send()
