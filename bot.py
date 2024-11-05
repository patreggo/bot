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
        print("Данные загружены успешно")
    except FileNotFoundError:
        chat_data = {}
        print("Файл данных не найден, создано новое хранилище")

# Сохранение данных в файл
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=4)
    print("Данные сохранены успешно")

# Функция для генерации случайного текстового сообщения
def generate_random_message(chat_id):
    messages_storage = chat_data.get(str(chat_id), {}).get('messages', [])
    if not messages_storage:
        return None

    message_fragments = []

    for _ in range(random.randint(2, 3)):
        message_data = random.choice(messages_storage)
        message_text = message_data['text']
        sender_name = message_data['sender']
        words = message_text.split()

        if len(words) > 0:
            start_index = 0
            fragment_length = random.randint(1, min(4, len(words)))
            fragment_text = ' '.join(words[start_index:start_index + fragment_length])
            message_fragments.append(f"{sender_name}: {fragment_text}")

    return ' '.join(message_fragments)

# Функция для генерации случайного стикера
async def generate_random_sticker(chat_id):
    stickers_storage = chat_data.get(str(chat_id), {}).get('stickers', [])
    if not stickers_storage:
        return None

    sticker_data = random.choice(stickers_storage)
    return InputDocument(
        id=sticker_data['id'],
        access_hash=sticker_data['hash'],
        file_reference=sticker_data['file_reference']
    )

@client.on(events.NewMessage)
async def store_message(event):
    global chat_data

    chat_id = str(event.chat_id)
    if chat_id not in chat_data:
        chat_data[chat_id] = {
            'messages': [],
            'stickers': [],
            'user_message_count': 0,
            'messages_interval': random.randint(7,18)
        }

    # Сохраняем сообщение или стикер
    if event.sticker:
        sticker = event.sticker
        chat_data[chat_id]['stickers'].append({
            'id': sticker.id,
            'hash': sticker.access_hash,
            'file_reference': sticker.file_reference
        })
        print(f"Стикер сохранен в чат {chat_id}")
    elif event.raw_text:
        chat_data[chat_id]['messages'].append({
            'text': event.raw_text,
            'sender': event.sender_id if event.sender_id else "Unknown"
        })
        print(f"Сообщение сохранено в чат {chat_id}")

    chat_data[chat_id]['user_message_count'] += 1

    # Проверяем, достигли ли мы интервала для этого чата
    if chat_data[chat_id]['user_message_count'] >= chat_data[chat_id]['messages_interval']:
        print("Достигнут интервал отправки случайного сообщения")

        # Отправляем случайный стикер или сообщение
        if random.choice([True, False]) and chat_data[chat_id]['stickers']:
            sticker = await generate_random_sticker(chat_id)
            if sticker:
                await client.send_file(event.chat_id, file=sticker)
                print("Отправлен случайный стикер")
        else:
            message = generate_random_message(chat_id)
            if message:
                await client.send_message(event.chat_id, message)
                print("Отправлено случайное сообщение:", message)
            else:
                print("Нет сообщений для отправки")

        # Сбрасываем счетчик и устанавливаем новый интервал
        chat_data[chat_id]['user_message_count'] = 0
        chat_data[chat_id]['messages_interval'] = random.randint(8, 18)

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

@client.on(events.NewMessage)
async def respond_to_keyword(event):
    keyword = 'хохлы'
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
