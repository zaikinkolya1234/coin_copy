
import telebot

TOKEN = "8432849665:AAEsa0PTkBzpYZae0y6fsxiq38bRtpLFGvo"
bot = telebot.TeleBot(TOKEN)

# Обработка команды /start
@bot.message_handler(commands=["start"])
def start(message):
    pass
bot.polling(none_stop=True)
