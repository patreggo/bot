import json
from datetime import datetime, timedelta
import re
from telethon.tl.types import InputDocument
from telethon import TelegramClient, events, types
import random
import spacy

# Telegram API
API_ID = '20853819'
API_HASH = 'baba4e824938a2abacff8f1af5deeb92'
BOT_TOKEN = '7304199579:AAEfU4_LfqYCF4r7udnLpwlK1_WabR1Bas8'
DATA_FILE = 'messages_data.json'

client = TelegramClient('TagAllBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Глобальная структура для хранения данных
chat_data = {}

ADMIN_USERS = ['gib00ba', 'EdwinPl2']

# Загружаем модель spaCy для обработки текста
nlp = spacy.load("ru_core_news_sm")

@client.on(events.NewMessage(pattern='/поставить на счетчик'))
async def set_period(event):
    sender = await event.get_sender()
    username = sender.username

    if username not in ADMIN_USERS:
        await event.reply("У вас нет прав для выполнения этой команды.")
        return

    args = event.raw_text.split()
    if len(args) != 5:
        await event.reply("Используйте: /поставить на счетчик @username дни")
        return

    target_username = args[3].lstrip('@')
    try:
        days = int(args[4])
        if days <= 0:
            raise ValueError("Период должен быть положительным числом.")
    except ValueError:
        await event.reply("Пожалуйста, укажите корректное количество дней.")
        return

    # Проверяем, есть ли пользователь в беседе
    chat = await event.get_chat()
    participants = await client.get_participants(chat)
    target_user = next((p for p in participants if p.username == target_username), None)

    if not target_user:
        await event.reply(f"Пользователь @{target_username} не найден в текущей беседе.")
        return

    # Устанавливаем период
    user_data = chat_data.setdefault(target_username, {})
    user_data['end_date'] = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    save_data()

    await event.reply(f"Период для @{target_username} установлен на {days} дней.")

# Проверка оставшегося времени
@client.on(events.NewMessage(pattern='/осталось'))
async def time_left(event):
    args = event.raw_text.split()
    if len(args) != 2:
        await event.reply("Используйте: /осталось @username")
        return

    target_username = args[1].lstrip('@')
    user_data = chat_data.get(target_username)

    if not user_data or 'end_date' not in user_data:
        await event.reply(f"Для пользователя @{target_username} не установлен период.")
        return

    end_date = datetime.strptime(user_data['end_date'], '%Y-%m-%d %H:%M:%S')
    remaining_time = end_date - datetime.now()

    if remaining_time.total_seconds() <= 0:
        await event.reply(f"Время для @{target_username} истекло.")
    else:
        days, seconds = divmod(remaining_time.total_seconds(), 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, _ = divmod(seconds, 60)
        await event.reply(f"Осталось {int(days)} дней, {int(hours)} часов, {int(minutes)} минут для @{target_username}.")

# Загрузка данных из файла
def load_data():
    global chat_data
    try:
        with open(DATA_FILE, 'r') as f:
            chat_data = json.load(f)
    except FileNotFoundError:
        chat_data = {}

# Сохранение данных в файл
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(chat_data, f)

# Генерация сообщения из частей других сообщений
def generate_random_message(chat_id, user_message=None):
    messages_storage = chat_data.get(str(chat_id), {}).get('messages', [])
    if not messages_storage:
        return None

    message_fragments = []

    if user_message:
        # Анализируем сообщение пользователя
        doc = nlp(user_message)
        keywords = [token.text for token in doc if token.pos_ in {"NOUN", "VERB"}]

        # Поиск сообщений, содержащих ключевые слова
        relevant_messages = [
            msg for msg in messages_storage
            if any(keyword in msg for keyword in keywords)
        ]

        # Если есть подходящие сообщения, используем их
        if relevant_messages:
            for _ in range(random.randint(2, 3)):
                message = random.choice(relevant_messages)
                doc = nlp(message)
                fragments = [token.text for token in doc if token.dep_ in {"nsubj", "obj", "ROOT"}]
                if fragments:
                    message_fragments.append(" ".join(fragments))
        else:
            # Если подходящих сообщений нет, выбираем случайные
            for _ in range(random.randint(2, 3)):
                message = random.choice(messages_storage)
                words = message.split()
                fragment_length = random.randint(1, min(5, len(words)))
                message_fragments.append(" ".join(words[:fragment_length]))
    else:
        # Если пользовательское сообщение не указано, генерируем как обычно
        for _ in range(random.randint(2, 3)):
            message = random.choice(messages_storage)
            doc = nlp(message)
            fragments = [token.text for token in doc if token.dep_ in {"nsubj", "obj", "ROOT"}]
            if fragments:
                message_fragments.append(" ".join(fragments))

    return " ".join(message_fragments)

# Хранение новых сообщений и автоматический ответ
@client.on(events.NewMessage)
async def store_message(event):
    global chat_data

    chat_id = str(event.chat_id)
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'messages': [],
            'user_message_count': 0,
            'messages_interval': random.randint(7, 17)  # Случайный интервал
        }

    if event.raw_text:
        chat_data[chat_id]['messages'].append(event.raw_text)
        chat_data[chat_id]['user_message_count'] += 1

        # Проверяем, нужно ли отправить сгенерированное сообщение
        if chat_data[chat_id]['user_message_count'] >= chat_data[chat_id]['messages_interval']:
            message = generate_random_message(chat_id)
            if message:
                await client.send_message(event.chat_id, message)

            # Сбрасываем счётчик
            chat_data[chat_id]['user_message_count'] = 0
            chat_data[chat_id]['messages_interval'] = random.randint(7, 17)

        save_data()

# Обработка ответа на сообщения бота
@client.on(events.NewMessage)
async def handle_reply_to_bot(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.sender_id == client.get_me().id:
            # Если сообщение является ответом боту
            user_message = event.raw_text
            chat_id = str(event.chat_id)

            # Генерация ответа с учётом сообщения пользователя
            response = generate_random_message(chat_id, user_message=user_message)
            if response:
                await client.send_message(event.chat_id, response)

# Получение ID чата
@client.on(events.NewMessage(pattern='/chatid'))
async def get_chat_id(event):
    await event.reply(f'Ваш ID чата: {event.chat_id}')

# Вывод информации о стикере
@client.on(events.NewMessage(pattern='стик'))
async def get_sticker_hash(event):
    if event.message.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.sticker:
            file_id = reply_message.sticker.id
            file_hash = reply_message.sticker.access_hash
            await event.reply(
                f'ID стикера: {file_id}\nHash стикера: {file_hash}\nFile Reference: {reply_message.sticker.file_reference}'
            )
        else:
            await event.reply('Пожалуйста, ответьте на сообщение с стикером.')
    else:
        await event.reply('Пожалуйста, используйте эту команду в ответ на сообщение с стикером.')

# Тег всех участников
@client.on(events.NewMessage(pattern='/all|@all|@everyone'))
async def tag_all(event):
    chat = await event.get_input_chat()
    participants = await client.get_participants(chat)

    mention_list = [f'@{participant.username}' for participant in participants if participant.username]

    for mention in mention_list:
        await client.send_message(chat, mention)


stickers = [
    {
        'id': 5213382276280231277,
        'hash': -5412342535908628580,
        'file_reference': b'\x01\x00\x00\x00"fj\xe9m\xd5\xc7O\xd0ey\x86)w\x03\t_\xe4\x9f\xee\xb3'
    },
    {
        'id': 5213042054740845429,
        'hash': 978015430433717147,
        'file_reference': b'\x01\x00\x00\x00/fj\xeb\x94\xda\xf5\xe2\xc0\xe5\x11\x01\x06k\xd3\xd2 f\xe9'
    }
]

@client.on(events.NewMessage)
async def respond_to_keyword(event):
    keyword = 'хохлы'  # Укажите ваше слово здесь
    pattern = rf'\b{keyword}\b'
    if re.search(pattern, event.raw_text, re.IGNORECASE):
        sticker = random.choice(stickers)
        await client.send_file(
            event.chat_id,
            file=InputDocument(
                id=sticker['id'],
                access_hash=sticker['hash'],
                file_reference=sticker['file_reference'],
            ),
            reply_to=event.message.id
        )

@client.on(events.NewMessage(pattern='/chatid'))
async def get_chat_id(event):
    await event.reply(f'Ваш ID чата: {event.chat_id}')

load_data()

if __name__ == '__main__':
    client.run_until_disconnected()