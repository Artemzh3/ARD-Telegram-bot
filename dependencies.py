import os

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from langchain_community.chat_models import GigaChat

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GIGA_TOKEN = os.getenv("GIGA_TOKEN")

giga = GigaChat(
    credentials=GIGA_TOKEN,
    verify_ssl_certs=False,
)

dp = Dispatcher()
bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def get_builder_markup_callback():
    builder_callback = InlineKeyboardBuilder()
    builder_callback.row(
        InlineKeyboardButton(text="Подробнее", callback_data="more_info"),
        InlineKeyboardButton(text="Кратче", callback_data="short_info"),
    )
    builder_callback.row(
        InlineKeyboardButton(text="Найти ещё похожее", callback_data="same_info"),
    )
    return builder_callback


list_not_to_builder_messages = [
    "Hello", "hello", "Bye", "bye", "Thanks", "thanks",
    "Goodbye", "goodbye", "Привет", "привет", "Пр", "пр",
]
