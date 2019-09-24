import requests
import json
from Recorder import record_audio, read_audio
import os, sys
from flask import Flask, request
from utils import wit_response
from pymessenger import Bot

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "EAAd8XPeSnFkBAMxkDccqVntZBPAdQTk0BZBCQdKrj7ZA8lqVVU46W8iZCvR5cDz6qDwyCkMdZAjB2c9DANuC05MaQSc5pLXzvfdMac3aomZCYV5wmHhSVEFYk2lgGIIx6T7IoVD0LssrUFMaCFAJGH4NbrgNRt70gbyIdR7QZAxCNZAJM5ZB92PJA"

bot = Bot(PAGE_ACCESS_TOKEN)

API_ENDPOINT = 'https://api.wit.ai/speech'
wit_access_token = 'IRAVCILZOTGRISND4XWHF6W6PEELRX4E'

def RecognizeSpeech(AUDIO_FILENAME, num_seconds = 12):
    
    record_audio(num_seconds, AUDIO_FILENAME)      
    audio = read_audio(AUDIO_FILENAME)       
    headers = {'authorization': 'Bearer ' + wit_access_token,
               'Content-Type': 'audio/wav'}  
    resp = requests.post(API_ENDPOINT, headers = headers,
                         data = audio)       
    data = json.loads(resp.content)  
    text = data['_text']  
    return text



@app.route('/', methods=['GET'])
def verify():
    # Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    #return "Hello world", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:

                # IDs
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    # Extracting text message
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = 'no text'

                    response = None

                    entity, value = wit_response(messaging_text)
                    if entity == 'newstype':
                        response = "Ok, I will send you the {} news".format(str(value))
                    elif entity == 'location':
                        response = "Ok, so you live in {0}. Here are top headlines from {0}".format(str(value))

                    if response == None:
                        response = "I have no idea what you are saying!"

                    bot.send_text_message(sender_id, response)

    return "ok", 200

def log(message):
    print(message)
    sys.stdout.flush()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    text =  RecognizeSpeech('myspeech.wav', 8)
    print("\nVous avez dit: {}".format(text))
