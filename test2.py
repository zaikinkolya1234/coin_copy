import telebot
from telebot import types

API_TOKEN = '7153665273:AAER0tnwXZO7xM1QP6Zb3UxuOgg8ZgZJEtI'
SUPPORT_CHAT_ID = -1002641880889  # ID форум-группы
ADMIN_ID = 1517971085  # ID админа

bot = telebot.TeleBot(API_TOKEN)

# Словари для работы
user_threads = {}             # user_id -> thread_id
first_message_sent = {}       # user_id -> bool
banned_users = set()          # user_id set

# 👉 Обработка личных сообщений от пользователей
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_user_message(message):
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name

    # 🚫 Проверка на бан
    if user_id in banned_users:
        return

    # 📌 Если темы нет — создаём
    if user_id not in user_threads:
        # Название темы будет равно имени пользователя
        topic_name = user_name
        forum_topic = bot.create_forum_topic(chat_id=SUPPORT_CHAT_ID, name=topic_name)
        user_threads[user_id] = forum_topic.message_thread_id
        first_message_sent[user_id] = False

        # Кнопка "Ban"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{user_id}"))

        intro_text = f"📩 Новое обращение от @{user_name} (ID: {user_id}):\n\n{message.text}"
        bot.send_message(chat_id=SUPPORT_CHAT_ID, message_thread_id=forum_topic.message_thread_id,
                         text=intro_text, reply_markup=markup)
        first_message_sent[user_id] = True
        return

    # 📨 Повторные сообщения
    thread_id = user_threads[user_id]
    text = message.text if first_message_sent.get(user_id, False) else f"📩 @{user_name}:\n\n{message.text}"
    first_message_sent[user_id] = True

    bot.send_message(chat_id=SUPPORT_CHAT_ID, message_thread_id=thread_id, text=text)

# 🔄 Обработка ответов админа в темах
@bot.message_handler(func=lambda msg: msg.chat.id == SUPPORT_CHAT_ID and msg.is_topic_message)
def handle_admin_reply(msg):
    thread_id = msg.message_thread_id
    user_id = next((uid for uid, tid in user_threads.items() if tid == thread_id), None)
    if user_id and user_id not in banned_users:
        try:
            bot.send_message(user_id, f"💬 {msg.text}")
        except Exception as e:
            bot.send_message(SUPPORT_CHAT_ID, f"⚠️ Не удалось отправить сообщение пользователю {user_id}:\n{e}")

# ⚙️ Обработка кнопки Ban
@bot.callback_query_handler(func=lambda call: call.data.startswith("ban_"))
def handle_ban_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Только админ может это сделать.")
        return

    user_id = int(call.data.split("_")[1])
    banned_users.add(user_id)
    bot.answer_callback_query(call.id, f"🚫 Пользователь {user_id} заблокирован.")
    bot.send_message(SUPPORT_CHAT_ID, f"🔒 Пользователь `{user_id}` больше не может писать.", parse_mode="Markdown")

bot.infinity_polling()
