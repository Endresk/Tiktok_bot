import logging
import sys

from database.Database import db
from texts import text_no_group
from keyboard import chat_and_markup, markup_administrator_1
from secret import TOKEN
from aiogram import Bot, F, Router
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, \
    ADMINISTRATOR, MEMBER, PROMOTED_TRANSITION, LEAVE_TRANSITION, Text, IS_MEMBER
from aiogram.types import ChatMemberUpdated, ReplyKeyboardMarkup, Message
from aiogram.utils.markdown import text as g

logging.basicConfig(stream=sys.stdout, level=logging.ERROR,
                    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", )

chats_variants = {
    "group": "группе",
    "supergroup": "супергруппе"
}

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))

bot = Bot(token=TOKEN)


async def user_status(event):
    status_user = (await bot.get_chat_member(event.chat.id, event.from_user.id)).status

    if status_user == 'creator':
        chat_member = 'creator'
        markup = markup_administrator_1
    elif status_user == 'administrator':
        chat_member = 'administrator'
        markup = markup_administrator_1
    else:
        chat_member = 'member'
        markup = ''

    return chat_member, markup


async def bot_as(event, text, chat_member, markup):
    if not await db.select_chats(event.chat.id):
        await db.insert_chat_id(event.chat.id)

    if not await db.select_users_anonymous(1087968824, event.chat.id):
        await db.insert_users_anonymous(1087968824, event.chat.id, chat_member)

    if not await db.select_users(event.from_user.id):
        await db.insert_users(event.from_user.id)

    if event.from_user.username != 'GroupAnonymousBot':
        if (await db.select_users(event.from_user.id))[0][1] == 0:
            await db.update_users_chat_add(event.from_user.id, event.chat.id, chat_member)
            chat_c_id = str(event.chat.id).replace('-100', '')
            chat_title = (await bot.get_chat(event.chat.id)).title
            await bot.send_message(chat_id=event.from_user.id,
                                   text=g(f'Группа: [{chat_title}](https://t\\.me/c/{chat_c_id}/1) '
                                          'добавлена для вас в использование\\.\n'
                                          f'{text}'),
                                   parse_mode="MarkdownV2",
                                   reply_markup=markup
                                   )
        elif (await db.select_users(event.from_user.id))[0][1] == event.chat.id:
            chat_c_id = str(event.chat.id).replace('-100', '')
            chat_title = (await bot.get_chat(event.chat.id)).title
            await bot.send_message(chat_id=event.from_user.id,
                                   text=g(f'Группа: [{chat_title}](https://t\\.me/c/{chat_c_id}/1) \n'
                                          f'{text}'),
                                   parse_mode="MarkdownV2",
                                   reply_markup=markup
                                   )

        else:

            chat_id = str(event.chat.id).replace('-100', '')
            await bot.send_message(
                chat_id=event.from_user.id,
                text=f'Бот в {chats_variants[event.chat.type]} '
                     f'"[{event.chat.title}\\!](https://t\\.me/c/{chat_id}/1)" \n'
                     f'{text}',
                parse_mode="MarkdownV2",
                reply_markup=markup
            )


# Назначение бота как администратора в группу
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated):
    chat_member, markup = await user_status(event)

    text = 'Бот добавлен вами как администратор'
    await bot_as(event, text, chat_member, markup)


# Назначение бота с какого то ранга (обычный, ограниченный, кикнутный) как администратора
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION))
async def bot_edit_as_admin(event: ChatMemberUpdated):
    chat_member, markup = await user_status(event)

    text = 'Бот назначен вами как администратор'
    await bot_as(event, text, chat_member, markup)


# Назначение бота как обычным участником в группу
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER))
async def bot_added_as_member(event: ChatMemberUpdated):
    chat_info = await bot.get_chat(event.chat.id)
    chat_member, markup = await user_status(event)

    text = 'Добавлен вами как обычный участник\n\n' \
           'Для работы, бота необходимо назначить администратором группы\\!'

    await bot_as(event, text, chat_member, markup)

    if not chat_info.permissions.can_send_messages:
        await bot.send_message(event.from_user.id, "У бота нет привилегий писать сообщения!!! \n "
                                                   "Необходимо назначить права!.")


# Удаление бота из группы
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_left_user(event: ChatMemberUpdated):
    if event.old_chat_member.status == 'member':
        status = ''
    elif event.old_chat_member.status == 'administrator':
        status = '\\(админ\\)'
    elif event.old_chat_member.status == 'restricted':
        status = '\\(ограниченный\\)'
    else:
        status = ''

    await db.delete_chats(event.chat.id)

    try:
        if await db.select_users_anonymous(1087968824, event.chat.id):
            await db.delete_user_anonymous(1087968824, event.chat.id)

        for i in await db.select_users_chat(event.chat.id):
            await db.update_users_chat(i[0], 0, 'member')
            markup = await chat_and_markup(event)

            try:
                await bot.send_message(chat_id=i[0],
                                       text=f'Бот{status} в {chats_variants[event.chat.type]} '
                                            f'"{event.chat.title}" удален\\!\n\n{text_no_group}',
                                       reply_markup=markup, parse_mode="MarkdownV2",
                                       disable_web_page_preview=True)
            except:
                logging.info(f"User current! Not Bot!")

    except:
        logging.info(f"User not found! Method del")
