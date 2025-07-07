import telebot
from utilitils.config import *


class Telegram:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN)
    
    def send(self, text):
        self.bot.send_message(5318464880, text)