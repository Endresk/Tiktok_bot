from database.Database import db
from secret import TOKEN
from texts import text_no_group
from keyboard import markup_administrator_1, markup_administrator_2
from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.utils.markdown import text as g

router = Router()
bot = Bot(token=TOKEN)


@router.message(Text(text='Разрешить всем участникам группы пользоваться ботом', ignore_case=True))
async def delete_group(message: Message):
    chat_id = (await db.select_users(message.from_user.id))[0][1]
    await db.update_chat_choice(chat_id, 1)

    await bot.send_message(chat_id=message.from_user.id,
                           text='Пользоваться ботом могут теперь все участники группы!',
                           reply_markup=markup_administrator_2)


@router.message(Text(text='Запретить всем участникам группы пользоваться ботом', ignore_case=True))
async def delete_group(message: Message):
    chat_id = (await db.select_users(message.from_user.id))[0][1]
    await db.update_chat_choice(chat_id, 0)

    for i in await db.select_users_chat(chat_id):
        print(i)
        if i[2] not in ('creator', 'administrator') and i[0] != 1087968824:
            await db.update_users_chat(message.from_user.id, chat_id, 'member')
            await message.answer(text='В группе запретили использовать бота!')

    await message.answer(text='Никто кроме владельца/администраторов не может пользоваться ботом!',
                         reply_markup=markup_administrator_1)
