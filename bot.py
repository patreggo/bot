from datetime import datetime

from telethon import TelegramClient, events, types

API_ID = '20853819'
API_HASH = 'baba4e824938a2abacff8f1af5deeb92'
BOT_TOKEN = '7304199579:AAEfU4_LfqYCF4r7udnLpwlK1_WabR1Bas8'

client = TelegramClient('TagAllBot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@client.on(events.NewMessage(pattern='/all'))
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


@client.on(events.NewMessage(pattern='дембель'))
async def time_until_19_june(event):
    now = datetime.now()
    target_date = datetime(now.year, 6, 19)

    # Если текущая дата позже 19 июня этого года, берем 19 июня следующего года
    if now > target_date:
        target_date = datetime(now.year + 1, 6, 19)

    time_left = target_date - now
    days_left = time_left.days
    hours_left = time_left.seconds // 3600
    minutes_left = (time_left.seconds % 3600) // 60

    await client.send_message(event.chat_id,
                              f'До дембеля осталось: {days_left} дней, {hours_left} часов и {minutes_left} минут.')



if __name__ == '__main__':
    client.run_until_disconnected()

if __name__ == '__main__':
    client.run_until_disconnected()
