import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dependencies import (
    bot,
    dp,
    giga,
    get_builder_markup_callback,
    list_not_to_builder_messages,
)


@dp.message(Command("start"))
async def start(message: Message) -> None:
    username = message.from_user.username
    if username is None:
        await message.answer(
            f"Привет, отправь мне свой вопрос и я помогу тебе! Подробности в моём описании."
        )
    else:
        await message.answer(
            f"Привет, <b>{username}</b>, отправь мне свой вопрос и я помогу тебе! Подробности в моём описании."
        )


@dp.message()
async def question(message: Message):
    await message.answer("Почти готово... 🤏")
    if type(message.text) != str:
        await message.answer("Я не могу это прочитать.")
    else:
        if message.text in list_not_to_builder_messages:
            response = giga.invoke(message.text)
            answer = response.content
            await bot.delete_message(
                message_id=message.message_id + 1,
                chat_id=message.chat.id,
            )
            await message.reply(
                f"Ответ: \n \n <b>{answer}</b>",
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Подробнее",
                    callback_data="more_info",
                ),
                InlineKeyboardButton(
                    text="Кратче",
                    callback_data="short_info",
                ),
            )
            builder.row(
                InlineKeyboardButton(
                    text="Найти похожее",
                    callback_data="same_info",
                )
            )

            response = giga.invoke(message.text)
            answer = response.content

            await bot.delete_message(
                message_id=message.message_id + 1, chat_id=message.chat.id
            )
            await message.reply(
                f"Ответ: \n \n <b>{answer}</b>",
                reply_markup=builder.as_markup(),
            )


@dp.callback_query(F.data == "more_info")
async def get_more_info(callback: CallbackQuery):
    response = giga.invoke(
        f"Напиши подробнее, но до 1000 символов: {callback.message.text}"
    )
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await callback.message.answer(
        f"Вот подробное содержание: \n \n <b>{response.content}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )


@dp.callback_query(F.data == "short_info")
async def get_more_info(callback: CallbackQuery):
    response = giga.invoke(f"Сократи этот текст: {callback.message.text}")
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await callback.message.answer(
        f"Вот краткое содержание: \n \n <b>{response.content}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )


@dp.callback_query(F.data == "same_info")
async def get_more_info(callback: CallbackQuery):
    response = giga.invoke(f"Найди похожее на эту тему: {callback.message.text}")
    await bot.delete_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
    )
    await callback.message.answer(
        f"Вот похожая тема: \n \n <b>{response.content}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )


async def main() -> None:
    await dp.start_polling(bot)


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    log.info("Bot has started")
    asyncio.run(main())
    log.info("Bot has stopped")
