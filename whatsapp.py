import os
import requests
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from flask import Flask, request

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter as chaves de API do Dify e do Twilio do arquivo .env
DIFY_API_KEY = os.getenv('DIFY_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# URL da API do Dify
DIFY_API_URL = 'https://api.dify.ai/v1'

# Função para obter a resposta do Dify
def get_dify_response(question):
    headers = {
        'Authorization': f'Bearer {DIFY_API_KEY}'
    }
    payload = {
        'question': question
    }
    response = requests.post(DIFY_API_URL, headers=headers, json=payload)
    return response.json()

# Função para enviar uma mensagem do WhatsApp usando o Twilio
def send_whatsapp_message(to, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
        to=f'whatsapp:{to}'
    )
    return message.sid

# Criar a aplicação Flask
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Obter a mensagem recebida via Twilio
    incoming_msg = request.form.get('Body', '').strip()
    from_number = request.form.get('From', '').strip()

    # Obter a resposta do Dify
    dify_response = get_dify_response(incoming_msg)

    # Extrair a resposta do Dify (supondo que a resposta esteja em 'answer')
    dify_answer = dify_response.get('answer', 'Desculpe, não consegui entender a sua pergunta.')

    # Criar a resposta para o Twilio
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(dify_answer)

    # Enviar a resposta via WhatsApp
    send_whatsapp_message(from_number, dify_answer)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
