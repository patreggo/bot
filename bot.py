from datetime import datetime
import re
import json
from telethon.tl.types import InputDocument
from telethon import TelegramClient, events, types
import random

API_ID = '20853819'
API_HASH = 'baba4e824938a2abacff8f1af5deeb92'
BOT_TOKEN = '7304199579:AAEfU4_LfqYCF4r7udnLpwlK1_WabR1Bas8'
DATA_FILE = 'messages_data.json'

client = TelegramClient('TagAllBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

chat_data = {}

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

# Функция для генерации сообщения из последовательных частей разных сообщений
def generate_random_message(chat_id):
    messages_storage = chat_data.get(str(chat_id), {}).get('messages', [])
    if not messages_storage:
        return None

    message_fragments = []

    # Выбираем 2-3 случайных сообщения и берем из них последовательные части
    for _ in range(random.randint(2, 3)):
        message = random.choice(messages_storage)  # Выбираем случайное сообщение
        words = message.split()  # Разбиваем сообщение на слова

        if len(words) > 0:  # Берем только те сообщения, где более 3 слов
            start_index = 0  # Начинаем с начала сообщения
            fragment_length = random.randint(1, min(4, len(words)))  # Длина фрагмента (от 3 до 7 слов)
            message_fragments.append(' '.join(words[start_index:start_index + fragment_length]))

    return ' '.join(message_fragments)  # Объединяем фрагменты в одно сообщение

@client.on(events.NewMessage)
async def store_message(event):
    global chat_data

    chat_id = str(event.chat_id)
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'messages': [],
            'user_message_count': 0,
            'messages_interval': random.randint(7, 15)  # Случайный интервал для этого чата
        }

    if event.raw_text:
        chat_data[chat_id]['messages'].append(event.raw_text)
        chat_data[chat_id]['user_message_count'] += 1

        # Проверяем, достигли ли мы интервала для этого чата
        if chat_data[chat_id]['user_message_count'] >= chat_data[chat_id]['messages_interval']:
            message = generate_random_message(chat_id)
            if message:
                await client.send_message(event.chat_id, message)  # Отправляем сообщение в тот же чат

            # Сбрасываем счетчик и устанавливаем новый интервал
            chat_data[chat_id]['user_message_count'] = 0
            chat_data[chat_id]['messages_interval'] = random.randint(3, 8)

        save_data()  # Сохраняем данные после каждого нового сообщения

@client.on(events.NewMessage(pattern='стик'))
async def get_sticker_hash(event):
    if event.message.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        if reply_message and reply_message.sticker:
            file_id = reply_message.sticker.id
            file_hash = reply_message.sticker.access_hash
            await event.reply(
                f'ID стикера: {file_id}\nHash стикера: {file_hash}\nFile Reference: {reply_message.sticker.file_reference}')
        else:
            await event.reply('Пожалуйста, ответьте на сообщение с стикером.')
    else:
        await event.reply('Пожалуйста, используйте эту команду в ответ на сообщение с стикером.')


@client.on(events.NewMessage(pattern='/all|@all|@everyone|Пойдете гулять?'))
async def tag_all(event):
    chat = await event.get_input_chat()
    participants = await client.get_participants(chat)

    # Собираем всех участников в строку
    mention_list = [f'@{participant.username}' for participant in participants if participant.username]

    for mention in mention_list:
        if mention_list:
            await client.send_message(chat, ''.join(mention))
        else:
            await client.send_message(chat, 'Не удалось найти участников для тега.')


@client.on(events.NewMessage(pattern='дембель|Дембель'))
async def time_until_19_june(event):
    now = datetime.now()
    target_date = datetime(now.year, 6, 19, 13)

    if now > target_date:
        target_date = datetime(now.year + 1, 6, 19)

    time_left = target_date - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    minutes_left = (time_left.seconds % 3600) // 60

    await client.send_message(event.chat_id,
                              f'До дембеля осталось: {days_left} дней, {hours_left} часов и {minutes_left} минут.')


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


# @client.on(events.NewMessage(pattern=r'.*хохлы.*'))
# async def handle_message(event):
#     sticker = random.choice(stickers)
#     await client.send_file(
#         event.chat_id,
#         file=InputDocument(
#             id=sticker['id'],
#             access_hash=sticker['hash'],
#             file_reference=sticker['file_reference'],
#         ),
#         reply_to=event.message.id
#     )


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