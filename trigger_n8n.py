import requests

url = "https://zezim123.app.n8n.cloud/webhook/08fde703-2b9c-49f0-9004-a27790505bae"
payload = {
    "mensagem": "Olá do VS Code! Integração funcionando 🚀"
}

try:
    response = requests.post(url, json=payload)
    print("Status:", response.status_code)
    print("Resposta:", response.text)
except Exception as e:
    print("Erro ao enviar requisição:", e)
