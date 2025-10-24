import asyncio
import logging

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dependencies import (
    bot,
    dp,
    giga,
    get_builder_markup_callback,
    list_not_to_builder_messages,
)

# --- ХРАНИЛИЩЕ КОНТЕКСТОВ ---
user_contexts = {}  # user_id -> list[str]


def add_to_context(user_id: int, message_text: str):
    """Добавляет сообщение (строку) в историю пользователя."""
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    user_contexts[user_id].append(message_text)
    # ограничим длину истории до 10 сообщений
    if len(user_contexts[user_id]) > 10:
        user_contexts[user_id] = user_contexts[user_id][-10:]


def get_context_text(user_id: int) -> str:
    """Возвращает историю сообщений как единый текст."""
    context = user_contexts.get(user_id, [])
    return "\n".join(context)


# --- ОБРАБОТЧИКИ ---


@dp.message(Command("start"))
async def start(message: Message) -> None:
    username = message.from_user.username or "друг"
    await message.answer(
        f"Привет, <b>{username}</b>! Меня зовут <b>ARD</b> 🤖\n"
        f"Отправь свой вопрос — я помогу 😉"
    )


@dp.message()
async def question(message: Message):
    user_id = message.from_user.id
    text = message.text

    if not isinstance(text, str):
        await message.answer("Я не могу это прочитать.")
        return

    # Добавляем сообщение пользователя в историю
    add_to_context(user_id, f"Пользователь: {text}")

    text_lower = text.lower().strip()

    # --- Проверка: если пользователь спрашивает "кто ты" или похожее ---
    who_phrases = [
        "кто ты",
        "кто ты такой",
        "что ты такое",
        "кто такой ard",
        "кто ты вообще",
        "кто ты бот",
        "кто ты есть",
        "who are you",
        "who r u",
        "what are you",
        "what is ard",
    ]
    if any(phrase in text_lower for phrase in who_phrases):
        await message.answer(
            "Я — <b>ARD</b> 🤖, твой виртуальный помощник. "
            "Отвечаю на вопросы, ищу информацию и просто могу поддержать беседу 😉"
        )
        add_to_context(user_id, "Бот: Я — ARD, твой виртуальный помощник 🤖")
        return

    # --- Быстрая реакция пользователю ---
    await message.answer("Думаю над ответом... 🤔")

    # --- Простые короткие фразы (без клавиатуры) ---
    if text_lower in list_not_to_builder_messages:
        response = giga.invoke(text)
        answer = response.content

        add_to_context(user_id, f"Бот: {answer}")

        try:
            await bot.delete_message(
                chat_id=message.chat.id, message_id=message.message_id + 1
            )
        except Exception:
            pass

        await message.reply(f"Ответ: \n\n<b>{answer}</b>")
        return

    # --- Обычные сообщения (с кнопками) ---
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Подробнее", callback_data="more_info"),
        InlineKeyboardButton(text="Кратче", callback_data="short_info"),
    )
    builder.row(InlineKeyboardButton(text="Найти похожее", callback_data="same_info"))

    context = get_context_text(user_id)
    response = giga.invoke(
        f"Вот история нашего диалога:\n{context}\n\n"
        f"Теперь ответь на последнее сообщение пользователя естественно и по контексту."
    )
    answer = response.content

    add_to_context(user_id, f"Бот: {answer}")

    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id + 1
        )
    except Exception:
        pass

    await message.reply(f"Ответ: \n\n<b>{answer}</b>", reply_markup=builder.as_markup())


# --- CALLBACKS ---


@dp.callback_query(F.data == "more_info")
async def handle_more_info(callback: CallbackQuery):
    original = callback.message.text or ""
    user_id = callback.from_user.id
    context = get_context_text(user_id)
    response = giga.invoke(
        f"Напиши подробнее, но до 1000 символов: {original}\n\nКонтекст:\n{context}"
    )
    answer = response.content

    try:
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
    except Exception:
        pass

    await callback.message.answer(
        f"Вот подробное содержание: \n\n<b>{answer}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )
    add_to_context(user_id, f"Бот: {answer}")


@dp.callback_query(F.data == "short_info")
async def handle_short_info(callback: CallbackQuery):
    original = callback.message.text or ""
    user_id = callback.from_user.id
    context = get_context_text(user_id)
    response = giga.invoke(f"Сократи этот текст: {original}\n\nКонтекст:\n{context}")
    answer = response.content

    try:
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
    except Exception:
        pass

    await callback.message.answer(
        f"Вот краткое содержание: \n\n<b>{answer}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )
    add_to_context(user_id, f"Бот: {answer}")


@dp.callback_query(F.data == "same_info")
async def handle_same_info(callback: CallbackQuery):
    original = callback.message.text or ""
    user_id = callback.from_user.id
    context = get_context_text(user_id)
    response = giga.invoke(
        f"Найди похожее на эту тему: {original}\n\nКонтекст:\n{context}"
    )
    answer = response.content

    try:
        await bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        )
    except Exception:
        pass

    await callback.message.answer(
        f"Вот похожая тема: \n\n<b>{answer}</b>",
        reply_markup=get_builder_markup_callback().as_markup(),
    )
    add_to_context(user_id, f"Бот: {answer}")


# --- ЗАПУСК ---
async def main() -> None:
    await dp.start_polling(bot)


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    log.info("Bot has started")
    asyncio.run(main())
    log.info("Bot has stopped")
