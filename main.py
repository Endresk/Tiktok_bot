import logging
import asyncio
import re
import sys

import nest_asyncio
from aiogram.fsm.strategy import FSMStrategy

from handlers import update_filter, modes
from participant import participant
from secret import TOKEN

from TikTok import tiktok

from database.Database import db
from keyboard import chat_and_markup
from texts import text_no_group, help_tiktok
from aiogram import Bot, types, F, Router, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import text as g, bold, code, hunderline
from aiogram.filters import Command, Text
from aiogram.types import Message

# логирование
logging.basicConfig(stream=sys.stdout, level=logging.ERROR,
                    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", )
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)

fh = logging.FileHandler("warning_log.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

warning_log.addHandler(fh)

bot = Bot(token=TOKEN)
router = Router()


# Проверка есть ли пользователь в бд его id, если нету, то добавляем и присваиваем ему режим 0,1,2
async def mode(message):
    s_user = await db.select_users(message.from_user.id)
    try:
        mode_ = s_user[0][1]
    except:
        await db.insert_users(message.from_user.id)
        mode_ = 0
    return mode_


# Проверка состоит ли бот в группе
async def check_bot(chat_id):
    try:
        gcm = await bot.get_chat_member(chat_id, 5762523028)
        csm_bot = gcm.can_send_messages
        cdm_bot = gcm.can_delete_messages
        status_bot = gcm.status
    except:
        cdm_bot = False
        csm_bot = False
        status_bot = 0

    return cdm_bot, csm_bot, status_bot


# Если бот состоит в группе как "админ" ? "имеет возможность писать сообщения" ? "удалять сообщения", тогда True
async def delete_message(message):
    cdm_bot, csm_bot, status_bot = await check_bot(message.chat.id)

    if status_bot == 'administrator':
        if csm_bot is None:
            if cdm_bot:
                await bot.delete_message(message.chat.id, message.message_id)
                h = True
            else:
                h = False
        else:
            h = False
    else:
        h = False

    return h


# Выполняется когда приходит сообщение из группы, то проверяется состояние бота и возможности писать всем,
# и статус пользователя
async def welcome_status(message, status_user):
    cdm_bot, csm_bot, status_bot = await check_bot(message.chat.id)

    if status_bot == 'administrator':
        if csm_bot is None:
            if cdm_bot:
                choice = (await db.select_chats(message.chat.id))[0][1]
                if status_user == 'creator':
                    await db.update_users_chat(message.from_user.id, message.chat.id, 'creator')
                    text_member = f'Приветствую\\! {message.from_user.first_name} \n\n{help_tiktok}'
                elif status_user == 'administrator':
                    await db.update_users_chat(message.from_user.id, message.chat.id, 'administrator')
                    text_member = f'Приветствую\\! {message.from_user.first_name} \n\n{help_tiktok}'
                else:
                    if choice == 1:
                        await db.update_users_chat(message.from_user.id, message.chat.id, 'member')
                        text_member = f'Приветствую\\! {message.from_user.first_name} \n\n{help_tiktok}'
                    else:
                        text_member = f'Приветствую\\! {message.from_user.first_name} \n' \
                                      f'В группе разрешено только администраторам группы присылать видео из TikTok'
                await message.answer(text=text_member, parse_mode="MarkdownV2")
            else:
                await message.answer(text=f'Приветствую\\! {message.from_user.first_name}\n'
                                          f'Бот неактивен!\n'
                                          f'Боту необходимо разрешение на удаление сообщений в группе!',
                                     parse_mode="MarkdownV2")
        else:
            await message.answer(text=f'Приветствую\\! {message.from_user.first_name}\n'
                                      f'Бот неактивен!\n'
                                      f'Боту необходимо разрешение писать сообщения в группе!',
                                 parse_mode="MarkdownV2")
    else:
        await message.answer(text=code('Бота необходимо назначить администратором группы!'),
                             parse_mode="MarkdownV2")


@router.message(Command(commands=["help"]))
async def cmd_help(message: types.Message):
    try:
        user_list = await db.select_users_anonymous(message.from_user.id, message.chat.id)
        user_chat_id = user_list[0][1]
    except:
        user_chat_id = 0

    if message.chat.id == message.from_user.id:
        select_user = await db.select_users(message.from_user.id)
        chat_id = select_user[0][1]

        if chat_id != 0:
            cdm_bot, csm_bot, status_bot = await check_bot(chat_id)
            chat_c_id = str(chat_id).replace('-100', '')
            chat_title = (await bot.get_chat(chat_id)).title
            if status_bot == 'administrator':
                if csm_bot is None:
                    if cdm_bot:

                        markup = await chat_and_markup(message)
                        select_user = await db.select_users(message.from_user.id)
                        chat_member = select_user[0][2]
                        chat_c_id = str(chat_id).replace('-100', '')
                        chat_title = (await bot.get_chat(chat_id)).title

                        if chat_member == 'member':
                            text_member = 'Обычный участник'
                            privileges = ''
                        elif chat_member == 'administrator':
                            text_member = 'Администратор'
                            privileges = g('\nСтатус позволяет всем участникам группы '
                                           'разрешить/запретить пользоваться ботом, '
                                           'для этого воспользуетесь соответствующим пунтом меню\\.')
                        elif chat_member == 'creator':
                            text_member = 'Владелец'
                            privileges = g('\nСтатус позволяет всем участникам группы '
                                           'разрешить/запретить пользоваться ботом, '
                                           'для этого воспользуетесь соответствующим пунтом меню\\.')
                        else:
                            text_member = ''
                            privileges = ''
                        await message.answer(
                            text=g(f'Группа: [{chat_title}](https://t\\.me/c/{chat_c_id}/1)\n'
                                   f'Cтатус \\-',
                                   bold(f'"{text_member}"\n'),
                                   f'{privileges}'
                                   ),
                            reply_markup=markup,
                            parse_mode="MarkdownV2",
                            disable_web_page_preview=True
                        )
                    else:
                        await message.answer(text=g(code('Боту необходимо разрешение на удаление сообщений в группе! '),
                                                    f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                             parse_mode="MarkdownV2")
                else:
                    await message.answer(text=g(code('Боту необходимо разрешение писать сообщения в группе! '),
                                                f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                         parse_mode="MarkdownV2")
            else:
                await message.answer(text=g(code('Бота необходимо назначить администратором группы! '),
                                            f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                     parse_mode="MarkdownV2")
        else:
            await message.answer(text=text_no_group, parse_mode="MarkdownV2", disable_web_page_preview=True)

    elif message.chat.id == user_chat_id:
        status_user = (await bot.get_chat_member(message.chat.id, message.from_user.id)).status

        await welcome_status(message, status_user)

    elif user_chat_id == 0:
        status_user = (await bot.get_chat_member(message.chat.id, message.from_user.id)).status

        if not await db.select_users(message.from_user.id):
            await db.insert_users_anonymous(message.from_user.id, message.chat.id, status_user)

        await welcome_status(message, status_user)


@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    if message.chat.id == message.from_user.id:
        if not await db.select_users(message.from_user.id):
            await db.insert_users(message.from_user.id)

        markup = await chat_and_markup(message)

        if not await db.select_users(message.from_user.id):
            await db.insert_users_anonymous(message.from_user.id, 0, 'member')

        await message.answer(g(f'Приветствую\\! {message.from_user.username}\n\n',
                               f'{help_tiktok}'
                               ),
                             reply_markup=markup,
                             parse_mode="MarkdownV2")


async def link_group(message, chat_id):
    cdm_bot, csm_bot, status_bot = await check_bot(chat_id)
    if chat_id != -1:
        chat_c_id = str(chat_id).replace('-100', '')
        chat_title = (await bot.get_chat(chat_id)).title
        if status_bot != 'left':
            if status_bot == 'administrator':
                if csm_bot is None:
                    if cdm_bot:
                        await participant(message, chat_id)
                    else:
                        await message.answer(text=g(code('Боту необходимо разрешение на удаление сообщений в группе! '),
                                                    f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                             parse_mode="MarkdownV2")
                else:
                    await message.answer(text=g(code('Боту необходимо разрешение писать сообщения в группе! '),
                                                f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                         parse_mode="MarkdownV2")
            else:
                await message.answer(text=g(code('Бота необходимо назначить администратором группы! '),
                                            f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                     parse_mode="MarkdownV2")
        else:
            await message.answer(text=g(code('Бота необходимо сначала добавить в группу! '),
                                        f'[{chat_title}](https://t\\.me/c/{chat_c_id}/1)'),
                                 parse_mode="MarkdownV2")
    elif chat_id == -1:
        await message.answer(text='Вы неверно указали ссылку или имя группы')
    else:
        markup = await chat_and_markup(message)
        await message.answer(text='Бот не состоит в группе!\n'
                                  'Необходимо сначала, что бы бот был в группе.', reply_markup=markup)


@router.message(F.text.regexp(r'@[^\s]+'))
async def echo_message(message: types.Message):
    # Выполняется только в боте
    if message.chat.id == message.from_user.id:
        try:
            chat_id = (await bot.get_chat(message.text)).id
        except:
            chat_id = -1
        await link_group(message, chat_id)


@router.message(F.text.regexp(r'https?://t.me/[^\s]+'))
async def echo_message(message: types.Message):
    # Выполняется только в боте
    if message.chat.id == message.from_user.id:
        try:
            if message.text.split('/')[-1].isdigit():
                digit_or_letter = message.text.split('/')[-2]
            else:
                text_qm = re.match(r'\w+?\?\w+?', message.text.split('/')[-1])
                if text_qm:
                    digit_or_letter = message.text.split('/')[-2]
                else:
                    digit_or_letter = message.text.split('/')[-1]

            if digit_or_letter.isdigit():
                chat_id = int(f'-100{digit_or_letter}')
            else:
                chat_id = (await bot.get_chat(f'@{digit_or_letter}')).id
        except:
            chat_id = -1
        await link_group(message, chat_id)


@router.message(F.text.regexp(r'https://[^\s]+tiktok.com/[^\s]+'))
async def echo_message(message: types.Message):
    try:
        user_list = await db.select_users_anonymous(message.from_user.id, message.chat.id)
        user_chat_id = user_list[0][1]
    except:
        user_chat_id = 0
    # Выполняется только в боте
    if message.chat.id == message.from_user.id:
        await tiktok(message, message.from_user.id)

    # Выполняется только в группе, если значение чата у пользователя
    # совпадает откуда пишет с тем который внесен в бд
    elif message.chat.id == user_chat_id:
        if await delete_message(message):
            await tiktok(message, message.chat.id)

    # Выполняется только в группе, если значение чата у пользователя 0
    elif user_chat_id == 0:
        if await delete_message(message):

            if not await db.select_chats(message.chat.id):
                await db.insert_chat_id(message.chat.id)

            if not await db.select_users_anonymous(1087968824, message.chat.id):
                await db.insert_users_anonymous(1087968824, message.chat.id, 'administrator')

            status_user = (await bot.get_chat_member(message.chat.id, message.from_user.id)).status
            if not await db.select_users(message.from_user.id):
                await db.insert_users_anonymous(message.from_user.id, message.chat.id, status_user)

            choice = (await db.select_chats(message.chat.id))[0][1]

            if status_user == 'creator':
                await db.update_users_chat(message.from_user.id, message.chat.id, 'creator')
                await tiktok(message, message.chat.id)
            elif status_user == 'administrator':
                await db.update_users_chat(message.from_user.id, message.chat.id, 'administrator')
                await tiktok(message, message.chat.id)
            else:
                if choice == 1:
                    await db.update_users_chat(message.from_user.id, message.chat.id, 'member')
                    await tiktok(message, message.chat.id)


async def main():
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.CHAT)

    dp.include_router(update_filter.router)
    dp.include_router(modes.router)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.run(main())
