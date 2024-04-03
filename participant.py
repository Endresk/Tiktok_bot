from aiogram import Bot
from database.Database import db
from secret import TOKEN
from keyboard import chat_and_markup, markup_administrator_1
from aiogram.utils.markdown import text as g

bot = Bot(token=TOKEN)


async def participant(message, chat_id):

    markup = await chat_and_markup(message)

    status_user = (await bot.get_chat_member(chat_id, message.from_user.id)).status
    chat_c_id = str(chat_id).replace('-100', '')
    chat_title = (await bot.get_chat(chat_id)).title

    if status_user == 'creator':
        text_chat = g(f'Группа "[{chat_title}](https://t\\.me/c/{chat_c_id}/1)" '
                      'добавлена для вас в использование\\.')
        markup = markup_administrator_1

    elif status_user == 'administrator':
        text_chat = g(f'Группа "[{chat_title}](https://t\\.me/c/{chat_c_id}/1)" '
                      'добавлена для вас в использование\\.')
        markup = markup_administrator_1

    elif status_user == 'left':
        text_chat = g('Либо включен "Anonymous" \\(выключите пожалуйста на время регистрации ботом и '
                      'повторите отправленное сообщение\\) \n'
                      'Либо вы не состоите в чате\\.')
    else:
        if await db.select_chats(chat_id):
            choice = (await db.select_chats(chat_id))[0][1]
            if choice == 0:
                text_chat = g('Администраторы группы не разрешили '
                              'пользоваться обычным участникам данным ботом\\.\n\n',
                              f'[Обратитесь к администраторам группы\\!](https://t\\.me/c/{chat_c_id}/1)')

            else:
                text_chat = g(f'Группа "[{chat_title}](https://t\\.me/c/{chat_c_id}/1)" '
                              'добавлена для вас в использование\\.')
        else:
            text_chat = g('Бот не состоит в группе!\n'
                          'Необходимо сначала, что бы бот был в группе.')
    await bot.send_message(chat_id=message.from_user.id,
                           text=text_chat,
                           parse_mode="MarkdownV2", reply_markup=markup)
