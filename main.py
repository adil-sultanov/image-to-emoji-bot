import telebot
import config

import os
import io

import requests
import random

from emojiDB import emojiDB

from io import BytesIO

from google.cloud import vision
from google.cloud.vision_v1 import types

bot = telebot.TeleBot(config.TOKEN)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.Google_credentials_key
client = vision.ImageAnnotatorClient()

feedback_list = {}

likelihood = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')
likelihood_value = {'UNKNOWN':-1, 'VERY_UNLIKELY':0, 'UNLIKELY':1, 'POSSIBLE':2, 'LIKELY':3, 'VERY_LIKELY':4}
    
@bot.message_handler(commands = ['start'])
def start(message):
    bot.send_message(message.chat.id, config.welcome, parse_mode = 'html')

@bot.message_handler(commands = ['about'])
def about(message):
    bot.send_message(message.chat.id, config.about, parse_mode = 'html')    

def get_URL(message):
    fileID = message.photo[-1].file_id
    file_url = bot.get_file(fileID).file_path
    URL = "https://api.telegram.org/file/bot" + config.TOKEN + "/" + file_url
    return URL

def get_image(URL):
    return BytesIO(requests.get(URL).content) 

@bot.message_handler(content_types = ['photo'])
def query(message):
    wait_message = bot.send_message(message.chat.id, "<em>It may take a moment, please wait...</em>", parse_mode = 'html')
    URL = get_URL(message)
    
    labels_info = client.label_detection(image = get_image(URL))
    faces_info = client.face_detection(image = get_image(URL))
    objects_info = client.object_localization(image = get_image(URL))
    
    objects = []
    for x in labels_info.label_annotations:
        label = x.description
        if label in emojiDB:
            objects.append(label)
    
    for x in objects_info.localized_object_annotations:
        obj = x.name
        if obj in emojiDB:
            objects.append(obj)
    
    unique_objects_list = []
    [unique_objects_list.append(x) for x in objects if x not in unique_objects_list]
    
    object_suggestions = ''
    for obj in unique_objects_list:
        object_suggestions += obj + ' - ' + emojiDB[obj] + '\n'

    if not unique_objects_list:
        object_suggestions = 'No objects were found.\n'
    
    face_detections = []
    for face_detection in faces_info.face_annotations:
        d = {
            'joy': likelihood[face_detection.joy_likelihood],
            'sorrow': likelihood[face_detection.sorrow_likelihood],
            'surprise': likelihood[face_detection.surprise_likelihood],
            'anger': likelihood[face_detection.anger_likelihood]
        }

        mx = 'joy'
        for key, value in d.items():
            if likelihood_value[value] > likelihood_value[d[mx]]:
                mx = key

        if likelihood_value[d[mx]] <= 0:
            mx = 'no expression'

        face_detections.append(emojiDB[mx])

    if not face_detections:
        face_suggestions = 'No human faces were found.'
    elif len(face_detections) == 1:
        face_suggestions = '1 face was found, suggested emojis are listed below:\n'
    else:
        face_suggestions = str(len(face_detections)) + ' faces were found, emoji suggestions for each one of them are listed below (in random order):\n'

    for suggestion in face_detections:
        emoji_list = [*suggestion]
        random.shuffle(emoji_list)
        face_suggestions += '•' + ''.join(emoji_list) + '\n'

    final_message = object_suggestions + '\n' + face_suggestions
    bot.delete_message(chat_id = wait_message.chat.id, message_id = wait_message.message_id)
    bot.send_message(message.chat.id, final_message)  
    
    if message.chat.id in feedback_list.keys() and feedback_list[message.chat.id] == True:
        try:
            feedback(message.chat.id)   
        except:
            pass
        
#begin of feedback part
def feedback(chatID):
    markup = telebot.types.InlineKeyboardMarkup(row_width = 3)
    item1 = telebot.types.InlineKeyboardButton('bad', callback_data = 'bad')
    item2 = telebot.types.InlineKeyboardButton('ok', callback_data = 'ok')
    item3 = telebot.types.InlineKeyboardButton('good', callback_data = 'good')
    markup.add(item1, item2, item3)
    bot.send_message(chatID, 'Please rate the suggestions relevance', reply_markup = markup)

@bot.message_handler(commands = ['feedback_mode'])
def feedback_switcher(message):
    chatID = message.chat.id;
    global feedback_list
    try:
        feedback_list[chatID] ^= 1
    except:
        feedback_list[chatID] = True

    if feedback_list[chatID] == True:
        bot.send_message(chatID, '<em>Feedback mode is on</em>', parse_mode='html')
    else:
        bot.send_message(chatID, '<em>Feedback mode is off</em>', parse_mode='html')

@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            bot.send_message(config.feedback_chatID, 'feedback: ' + call.data)
            bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)
            bot.send_message(call.message.chat.id, "<em>Thank you for your response!</em>", parse_mode = 'html')
    except Exception as e:
        print(repr(e))

#end of feedback part


bot.polling(none_stop = True)
