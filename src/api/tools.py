import re
import json


def create_chat_message(msg_template):
  message = ''
  message_items = re.split(r'(:\w+:)', msg_template)
  emotes = re.findall(r'(:\w+:)', msg_template)

  for item in message_items:
    if item in emotes:
      with open('/app/src/api/emotes.json', 'r') as emotes_json_file:
        emotes_json, emote = json.load(emotes_json_file), item[1:-1]
        if emote in emotes_json:
          emote_src = emotes_json[emote]
          message += f'<img src="{emote_src}" class="user-message-emote">'
        else:
          message += f'<span class="user-message-item">{item}</span>'
    else:
      message += f'<span class="user-message-item">{item}</span>'

  return message
