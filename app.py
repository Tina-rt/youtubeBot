from flask import Flask, request, url_for, send_from_directory
import requests
import sys
import json
from pprint import pprint as pp
from videoInfo import *
from requests_toolbelt import MultipartEncoder
import os
from threading import Thread
from string_res import *
import random


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def isGreetings(s):
	for g in GREETINGS:
		if s.lower() in g or s.lower() == g or g in s.lower():
			return True
	return False

ACCESS_TOKEN = 'EAAGoQuCCAo8BAIoE9ZCChkBlvuR3Radvmdky3pgr41dQZAQLqNhX6jI3SG301ERjZBQoV8sQU2kP7N68ffRRZCJv1nzDPFSyxiD97nWmhXY7ov3ZAc3F6SbWZCnIEgb9de7F5DnZBSZC2PJrsYUZC11dCRz1WRNY3miIsQcU4BFIZAmfK6b3RtsZCSZC'
# ACCESS_TOKEN = 'EAA1wRuSPHuIBADjv4nmhWBWzFn78QFffqXZAyf5Sy0oxfH8F21Pqc3IRyURuHmADUNBJ5WqaJsoEelSFyzaLZAIZBuZAYHwaDZBNnAwRp7OFmkEYZCM7Yq9iYLXhKZANFtS5rEiySIeCZCIZAF6xZCaGDcGYnOxj1klR49VY861VS38wNl27LMromP'
URL = 'https://graph.facebook.com/v2.6/me/messages?access_token='+ACCESS_TOKEN
# myUrl = 'https://htbot2001.herokuapp.com'
myUrl = 'https://tinatina.pythonanywhere.com/'
# myUrl = 'https://998a1cbff7e0.ngrok.io'


def typing_on(dest_id):
	# print('typing_on')
	obj = {
	  "recipient": {
	    "id": dest_id
	  },
	  "sender_action": "typing_on"
	}
	headers = {"Content-Type": "application/json"}
	r = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" +
	                  ACCESS_TOKEN, data=json.dumps(obj), headers=headers)


def typing_off(dest_id):
	# print('typing_on')
	obj = {
	  "recipient": {
	    "id": dest_id
	  },
	  "sender_action": "typing_off"
	}
	headers = {"Content-Type": "application/json"}
	r = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" +
	                  ACCESS_TOKEN, data=json.dumps(obj), headers=headers)


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    if request.args.get("hub.mode") == "subscribe" and request.args.get('hub.challenge'):
        if not request.args.get('hub.verify_token') == 'hello':
            return 'Verification token mismatch', 403
        return request.args['hub.challenge'], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    # print(url_for('static', filename='video.mp4'))
    data = request.get_json()
    log(data)
    # typing_off()
    for entry in data['entry']:
        for messaging_event in entry['messaging']:
            # print(messaging_event)
            sender_id = messaging_event['sender']['id']
            # typing_on(sender_id)

            if 'message' in messaging_event:
                if 'text' in messaging_event['message'] and 'quick_reply' not in messaging_event['message']:
                    query = messaging_event['message']['text']
                    if isGreetings(query):
                        sendText(sender_id, GREETINGS_REPLY[0])
                        typing_off(sender_id)
                    else:

                        list_video = getListVideo(query, 1)
                        # pp(list_video)
                        if len(list_video) > 0:

                            send_video_suggestion(sender_id, list_video, 1, query)
                            typing_off(sender_id)
                if 'quick_reply' in messaging_event['message']:
                	payload = messaging_event['message']['quick_reply']['payload']
                	payload = json.loads(payload)
                	print(payload['page'])
                	page = payload['page']
                	list_video = getListVideo()

            elif 'postback' in messaging_event:
                if 'payload' in messaging_event['postback']:
                    pload = messaging_event['postback']['payload']
                    if is_json(pload):
                        pload_json = json.loads(pload)
                        print(pload_json)
                        if 'watch' in pload_json:
                            video_url = pload_json['watch']

                            sendText(
                                sender_id, 'Envoi de la video... (Cela peut prendre 5mn)')
                            # typing_on(sender_id)
                            th1 = Thread(target=lambda: send_video(
                                sender_id, video_url, ), daemon=True)
                            th1.start()

                            print('reach')
                            return 'ok', 200
                        elif 'listen' in pload_json:
                            y_url = pload_json['listen']
                            sendText(sender_id, 'Envoi de l\'audio ...')
                            try:

                                # downloadAudio(y_url, sender_id)
                                th = Thread(target=lambda: send_audio(
                                    sender_id, y_url), daemon=True)
                                th.start()
                            except FileSizeOver:
                                sendText(
                                    sender_id, 'La taille de \'audio est trop grande... choisissez une video d\'une duree inferieur a 10mn')
                    elif 'help' == pload:
                        sendText(
                            sender_id, 'Rechercher des videos sur YouTube en envoyant vos mots cle \n Exemple: Ariana Grande positions, Agrad hafatra, ...')
                    elif 'CREDIT' == pload:
                        sendText(sender_id, CREDIT)
                    elif 'get_started' == pload:
                    	sendText(sender_id, GREETINGS_REPLY[0])

                # engine = VideosSearch(query, limit=4)
            # typing_off(sender_id)
    return 'ok', 200


@app.route('/download/<filename>')
def get_file(filename):
    """Download a file."""
    print(filename)
    return send_from_directory('.', filename, as_attachment=True)



def send_audio(dest_id, audio_url):
    typing_on(dest_id)
    sendText(dest_id, 'Telechargement...')
    print(audio_url)
    yt = YouTube(audio_url)
    st = yt.streams.filter(only_audio=True)
    # print(st)
    pp(st)
    # st = st[0]
    # # st = yt.streams.first()
    # # pp(list(t))
    for s in st:
        print('filesize', s.filesize)
        if s.filesize > 25_000_000:
            if s == st[-1]:
                sendText(dest_id, 'Le fichier est trop grande')

            continue

            # raise FileSizeOver("File is over than 25mb")
        path, basename = os.path.split(s.download(filename=dest_id))
        os.rename(f'{basename}', f'{dest_id}.mp3')

        url = f'{myUrl}/download/{dest_id}.mp3'
        print(url)

        data = {
            "recipient": {
                "id": f"{dest_id}"
            },
            "message": {
                "attachment": {
                    "type": "audio",
                    "payload": {
                        "url": f"{url}",
                        "is_reusable": 'true'
                    }
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post("https://graph.facebook.com/v10.0/me/messages?access_token=" +
                          ACCESS_TOKEN, data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            print(r, 'requset content', r.content)
            sendText(dest_id, 'Tapez votre rechereche sur Youtube...')
            break
    typing_off(dest_id)
    sys.exit()


def send_video(dest_id, video_url):
    typing_on(dest_id)
    sendText(dest_id, 'Telechargement...')
    # try:
    downloadVideo(video_url, dest_id)

    url = f'{myUrl}/download/{dest_id}.mp4'
    print(url)
    # try:
    data = {
        "recipient": {
            "id": f"{dest_id}"
        },
        "message": {
            "attachment": {
                "type": "video",
                "payload": {
                    "url": f"{url}",
                    "is_reusable": 'true'
                }
            }
        }
    }

    headers = {"Content-Type": "application/json"}
    r = requests.post("https://graph.facebook.com/v10.0/me/messages?access_token=" +
                      ACCESS_TOKEN, data=json.dumps(data), headers=headers)
    print(r, 'requset content', r.content)
    sendText(dest_id, 'Tapez votre rechereche sur Youtube...')
    # except FileSizeOver:
    #     sendText(
    #         dest_id, 'La taille est trop grande, choisissez une video plus courte inferieur a 8mn')
    # except Exception as e:
    # 	print(e)
    # 	sendText('3122189294503199', e)
    # 	sendText(dest_id, 'Une erreur s\'est produite')
    typing_off(dest_id)
    sys.exit()
    # sendText(dest_id, 'ok')


def sendText(dest_id, text):
    typing_on(dest_id)
    data = {
        "recipient": {
            "id": f"{dest_id}"
        },
        "messaging_type": "RESPONSE",
        "message": {
            "text": f"{text}",

        }
    }
    headers = {"Content-Type": "application/json"}
    r = requests.post(URL, data=json.dumps(data), headers=headers)
    typing_off(dest_id)

def send_response_quickreply(dest_id, reply, payloads):
	# print(reply)
	data = {
	  "recipient":{
	    "id":f"{dest_id}"
	  },
	  "messaging_type": "RESPONSE",
	  "message":{
	    # "text": f"{reply}",
	    "quick_replies": payloads
	    
	  }
	}
	headers = {"Content-Type": "application/json"}
	r = requests.post(URL, data=json.dumps(data), headers=headers)
	print(r.content)

def send_video_suggestion(dest_id, list_video, page):
    typing_on(dest_id)
    current_list_video = list_video[:4]
    print(current_list_video)
    data = {
        "recipient": {
            "id": f'{dest_id}'
        },
        "messaging_type": "response",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": f"{video['title']}",
                            "image_url": f"{video['thumbnail']}",
                            "subtitle": f"{video['duration']} - {video['viewCount']['short']}",

                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Regarder",
                                    "payload": json.dumps({
                                        'watch': video['url']
                                    })
                                }, {
                                    "type": "postback",
                                    "title": "Ecouter",
                                    "payload": json.dumps({
                                        'listen': video['url']
                                    })
                                }
                            ]
                        } for video in current_list_video
                    ]
                },
                
            },
            "quick_replies": [
                {	
	                'content_type': 'text',
		    		'title': 'Page suivante',
		    		'payload': json.dumps({
		    			'page': page+1,
		    			'query': query
		    			})
    			}
            ]
            
        }
    }

    # send_response_quickreply(dest_id, '', [
    # 	{	'content_type': 'text',
    # 		'title': 'Page suivante',
    # 		'payload': json.dumps({'page': page+1})
    # 	}
    # ])

    # data['message']['quick_reply'] = [
    # 	{	'content_type': 'text',
    # 		'title': 'Page suivante',
    # 		'payload': {'page': page+1}
    # 	}
    # ]

    headers = {"Content-Type": "application/json"}
    r = requests.post(URL, data=json.dumps(data), headers=headers)
    typing_off(dest_id)
    print(r.content)

def log(message):
    pp(message)
    sys.stdout.flush()


def sendRaw(data):
    headers = {"Content-Type": "application/json"}
    r = requests.post('https://graph.facebook.com/v10.0/me/messenger_profile?access_token=' +
                      ACCESS_TOKEN, data=json.dumps(data), headers=headers)
    print(r.content)

data = {
    "get_started": {
        "payload": "get_started"
    }
}
# sendRaw(data)

# sendRaw({
#     "persistent_menu": [
#         {
#             "locale": "default",
#             "composer_input_disabled": "false",
#             "call_to_actions": [
#                 {
#                     "type": "postback",
#                     "title": "Aide",
#                     "payload": "help"
#                 },
#                 {
#                     "type": "postback",
#                     "title": "Credit",
#                     "payload": "CREDIT"
#                 },

#                 #     {
#                 #         "type": "web_url",
#                 #         "title": "Contact",
#                 #         "url": "https://www.facebook.com/profile.php?id=100008494414113/app=fbl",
#                 #         "webview_height_ratio": "full"
#                 #     }
#                 # ]
#             ]}
#     ]
# })
def send_file(recipient_id, file_path):
    '''Send file to the specified recipient.
    https://developers.facebook.com/docs/messenger-platform/send-api-reference/file-attachment
    Input:
        recipient_id: recipient id to send to
        file_path: path to file to be sent
    Output:
        Response from API as <dict>
    '''
    payload = {
        'recipient': json.dumps(
            {
                'id': recipient_id
            }
        ),
        'message': json.dumps(
            {
                'attachment': {
                    'type': 'file',
                    'payload': {}
                }
            }
        ),
        'filedata': '@/home/tina/Documents/youtube bot/fichier'
    }
    # multipart_data = MultipartEncoder(payload)
    # multipart_header = {
    #     'Content-Type': multipart_data.content_type
    # }
    headers = {"Content-Type": "application/json"}
    r = requests.post('https://graph.facebook.com/v10.0/me/messages?access_token='+ACCESS_TOKEN, data=json.dumps(payload), headers=headers)
    print(r.content)
# send_file('3122189294503199', 'fichier')
# from pymessenger.bot import Bot
# bot = Bot(ACCESS_TOKEN)
# print(bot.send_file('3122189294503199', 'fichier'))
if __name__ == '__main__':
    app.run()
