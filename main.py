import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
import os

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Загружаем вопросы
with open("fixed_questions_cleaned.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

user_states = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    await send_question(message.chat.id)

async def send_question(chat_id):
    question = random.choice(questions)
    user_states[chat_id] = question

    variants_text = ""
    for i, option in enumerate(question["options"]):
        variants_text += f"{chr(65+i)}) {option}\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=chr(65+i), callback_data=str(i))] for i in range(len(question["options"]))
    ])

    await bot.send_message(chat_id, f"<b>❓ {question['question']}</b>\n\n{variants_text}", reply_markup=keyboard)

@dp.callback_query(F.data)
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected_index = int(callback.data)
    question = user_states.get(user_id)

    if question:
        correct_index = question["correct_option_index"]
        selected_letter = chr(65 + selected_index)
        selected_text = question["options"][selected_index]

        if selected_index == correct_index:
            response = f"✅ <b>To‘g‘ri javob!</b>\nSiz tanladingiz: <b>{selected_letter}) {selected_text}</b>"
        else:
            correct_letter = chr(65 + correct_index)
            correct_text = question["options"][correct_index]
            response = f"❌ <b>Noto‘g‘ri</b>\nSiz tanladingiz: <b>{selected_letter}) {selected_text}</b>\nTo‘g‘ri javob: <b>{correct_letter}) {correct_text}</b>"

        await callback.answer()
        await bot.send_message(user_id, response)
        await send_question(user_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
