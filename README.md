# Image-to-emoji telegram bot
## Description
Telegram bot that can suggest emojis by photo sent using Google Cloud Vision API. It scans for key objects and human faces. Emoji suggestions are based on Google Cloud Vision API label detection, face detection and object localization methods.

## How to use
Go to https://t.me/imagetoemoji_bot and type /start to begin.

## How to setup your own bot copy
Download project files and place them in the same folder. Install following python libraries:

```
google-cloud-vision
pyTelegramBotAPI
requests
```

Go to https://console.cloud.google.com/. Create project, enable API and create credentials. Download credentials key file (.json) and place it in the folder with other project files. Change values of **Google_credentials_key** and **TOKEN** variables in _config.py_ to your credentials key and telegram bot token, respectively. Run _main.py_.


## Contacts
Telegram: https://t.me/vonatlus

Email: sultanov.adil05@gmail.com

