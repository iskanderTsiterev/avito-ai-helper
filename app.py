import asyncio
import sqlite3
import io
import base64
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from openai import OpenAI
from PIL import Image

# =====================================================================
# НАСТРОЙКА КЛЮЧЕЙ И ОКРУЖЕНИЯ (ИСПРАВЛЕНО)
TELEGRAM_TOKEN = "8806610748:AAEZ5xoHAAzc4PGuHXoGQG4O60MeaCoMSH4"
VSEGPT_API_KEY = "sk-or-vis-3f43b679667f339cf3bf0299f01037887e50085a53bebc26" 
FREE_LIMIT = 5  # Дневной лимит запросов
# =====================================================================

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Подключаем стабильный шлюз к Gemini 2.5 Flash без необходимости VPN
ai_client = OpenAI(
    base_url="https://vsegpt.ru",
    api_key=VSEGPT_API_KEY
)

text_history = {}

# --- РАБОТА С БАЗОЙ ДАННЫХ (ИСПРАВЛЕНО) ---
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            requests_today INTEGER DEFAULT 0,
            last_request_date TEXT,
            is_premium INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_or_create_user(user_id, username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT requests_today, last_request_date, is_premium FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user is None:
        cursor.execute("INSERT INTO users (user_id, username, requests_today, last_request_date, is_premium) VALUES (?, ?, 0, ?, 0)", (user_id, username, today))
        conn.commit()
        conn.close()
        return {"requests_today": 0, "is_premium": 0}
    else:
        requests_today, last_request_date, is_premium = user
        if last_request_date != today:
            # Если наступил новый день, сбрасываем счетчик лимитов
            cursor.execute("UPDATE users SET requests_today = 0, last_request_date = ? WHERE user_id = ?", (today, user_id))
            conn.commit()
            conn.close()
            return {"requests_today": 0, "is_premium": is_premium}
        else:
            conn.close()
            return {"requests_today": requests_today, "is_premium": is_premium}

def increment_requests(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET requests_today = requests_today + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def activate_premium_db(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_premium = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- КНОПКИ ---
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="👤 Мой Профиль")
    builder.button(text="⭐ Купить Premium")
    builder.button(text="🧹 Очистить контекст")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# --- ОБРАБОТЧИКИ COMMANDS ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    get_or_create_user(message.from_user.id, message.from_user.username)
    text_history[message.from_user.id] = "" 
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🚀\n"
        f"Я твой ИИ-Оценщик хлама и личный ассистент.\n\n"
        f"📸 **Просто отправь мне фото любой вещи**, и я рассчитаю её стоимость и подготовлю объявление на Авито!",
        reply_markup=get_main_keyboard()
    )

@dp.message(F.text == "👤 Мой Профиль")
async def cmd_profile(message: types.Message):
    user_data = get_or_create_user(message.from_user.id, message.from_user.username)
    status = "👑 Премиум аккаунт" if user_data["is_premium"] else "🆓 Бесплатный тариф"
    left_requests = "∞" if user_data["is_premium"] else max(0, FREE_LIMIT - user_data["requests_today"])
    await message.answer(
        f"👤 **Ваш профиль в системе:**\n├ Статус: {status}\n└ Осталось оценок на сегодня: **{left_requests}**"
    )

@dp.message(F.text == "🧹 Очистить контекст")
async def cmd_clear_context(message: types.Message):
    text_history[message.from_user.id] = ""
    await message.answer("🧹 **История диалога успешно очищена!**")

@dp.message(F.text == "⭐ Купить Premium")
async def cmd_buy_premium(message: types.Message):
    await message.answer_invoice(
        title="👑 Premium статус Оценщика",
        description="Активирует полный безлимит на оценку вещей по photo на 30 дней!",
        payload="premium_subscription",
        provider_token="",  
        currency="XTR",     
        prices=[types.LabeledPrice(label="Premium 30 дней", amount=50)] 
    )

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    activate_premium_db(message.from_user.id)
    await message.answer(
        f"🎉 **Ура! Оплата прошла успешно!**\n👑 Вам выдан статус **Premium** на 30 дней. Все лимиты сняты!"
    )

# --- ИСПРАВЛЕННАЯ ОБРАБОТКА ФОТО (Google Gemini 2.5 Flash со зрением без VPN) ---
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    user_data = get_or_create_user(message.from_user.id, message.from_user.username)
    if not user_data["is_premium"] and user_data["requests_today"] >= FREE_LIMIT:
        await message.reply("⚠️ Вы исчерпали лимит бесплатных запросов! Нажмите кнопку **⭐ Купить Premium**, чтобы снять ограничения.")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        photo = message.photo[-1]
        file_in_io = io.BytesIO()
        await bot.download(photo, destination=file_in_io)
        file_in_io.seek(0)
        
        # Сжимаем фото перед отправкой, чтобы прокси-сервер не сбоил
        image = Image.open(file_in_io)
        image.thumbnail((800, 800))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=80)
        
        img_bytes = buffered.getvalue()
        img_str = base64.b64encode(img_bytes).decode('utf-8')
        
        system_instruction = """
        Ты — профессиональный ИИ-оценщик вторичного рынка (Авито) и копирайтер.
        Изучи прикрепленное изображение товара. Определи бренд и модель по фото.
        Выдай подробный ответ на РУССКОМ языке по блокам:
        📊 БЛОК 1: АНАЛИЗ СТОИМОСТИ (Рекомендуемая цена, вилка цен от минимальной до максимальной).
        📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ АВИТО (Цепляющий заголовок, структурированный текст, блок доставки, призыв к действию).
        """
        
        # Запрос к зрячей Gemini 2.5 Flash через ВсеGPT
        response = ai_client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_instruction},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                    ]
                }
            ]
        )
        
        if isinstance(response, str):
            ai_text = response
        elif hasattr(response, 'choices') and len(response.choices) > 0:
            ai_text = response.choices.message.content
        else:
            ai_text = str(response)
        
        if ai_text and "<!DOCTYPE html>" not in ai_text:
            if not user_data["is_premium"]:
                increment_requests(message.from_user.id)
            await message.reply(ai_text)
        else:
            await message.reply("Не удалось распознать изображение. Попробуйте отправить другое фото.")
            
    except Exception as e:
        await message.reply("Ошибка ИИ при сканировании фото.")
        print(f"Ошибка фото: {e}")

# --- ТЕКСТОВЫЙ ЧАТ (ИСПРАВЛЕНО) ---
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_data = get_or_create_user(message.from_user.id, message.from_user.username)
    if not user_data["is_premium"] and user_data["requests_today"] >= FREE_LIMIT:
        await message.reply("⚠️ Лимит исчерпан! Купите Premium статус.")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        response = ai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты — ИИ-помощник по расхламлению дома. Отвечай коротко и по делу на русском языке."},
                {"role": "user", "content": message.text}
            ]
        )
        if isinstance(response, str):
            ai_text = response
        elif hasattr(response, 'choices') and len(response.choices) > 0:
            ai_text = response.choices.message.content
        else:
            ai_text = str(response)
            
        if not user_data["is_premium"]:
            increment_requests(message.from_user.id)
        await message.reply(ai_text)
    except Exception as e:
        await message.reply("Ошибка ИИ при обработке текста.")
        print(f"Ошибка текста: {e}")

async def main():
    init_db()
    print("🚀 Бот-оценщик на aiogram 3.x с ИИ-Зрением Gemini запущен успешно!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
