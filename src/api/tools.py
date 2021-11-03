import re
import json


def create_chat_message(msg_template):
  message = ''
  message_items = re.split(r'(:\w+:)', msg_template)
  emotes = re.findall(r'(:\w+:)', msg_template)

  for item in message_items:
    if item in emotes:
      with open('./emotes.json', 'r') as emotes_json:
        emote_src = json.load(emotes_json)[item[1:-1]]
      message += f'<img src="{emote_src}" class="user-message-emote">'
    else:
      message += f'<span class="user-message-item">{item}</span>'

  return message
