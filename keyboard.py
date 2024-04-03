from database.Database import db
from aiogram import types


markup_2 = [

    [
        types.KeyboardButton(text='Разрешить всем участникам группы пользоваться ботом')
    ]

]
markup_administrator_1 = types.ReplyKeyboardMarkup(keyboard=markup_2, resize_keyboard=True)

markup_2_2 = [

    [
        types.KeyboardButton(text='Запретить всем участникам группы пользоваться ботом')
    ]
]
markup_administrator_2 = types.ReplyKeyboardMarkup(keyboard=markup_2_2, resize_keyboard=True)


async def chat_and_markup(message):
    if message.chat.id == message.from_user.id:
        chat_list = await db.select_users(message.chat.id)
        chat_id = chat_list[0][1]
        chat_member = chat_list[0][2]

        if chat_list[0][0] != 1087968824:
            if chat_id == 0:
                markup = ''
            else:
                if chat_member in ('creator', 'administrator'):
                    chat = await db.select_chats(chat_id)
                    choice = chat[0][1]
                    if chat[0][0]:
                        if choice == 1:
                            markup = markup_administrator_2
                        else:
                            markup = markup_administrator_1
                    else:
                        markup = markup_administrator_1
                else:
                    markup = ''
        else:
            markup = ''

        return markup
