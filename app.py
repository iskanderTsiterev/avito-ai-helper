import streamlit as st
import requests
from PIL import Image
import io
import base64

# Настройка интерфейса сайта в браузере
st.set_page_config(page_title="Авито Расхламление с ИИ", page_icon="✨", layout="centered")

# --- ГЛАВНЫЙ БАННЕР И МАРКЕТИНГОВЫЙ ЗАГОЛОВОК ---
st.title("✨ Преврати ненужный хлам в чистые деньги!")
st.subheader("Освободи место в доме и заработай на этом с помощью ИИ")
st.markdown("""
У каждого в доме есть вещи, которые лежат без дела: остатки стройматериалов после ремонта, 
старая техника, надоевший парфюм или одежда. **Пора превратить этот мусор в свободное пространство и рубли на карте!**

Наш искусственный интеллект мгновенно проанализирует рынок вторички РФ, 
выдаст точную стоимость вещи и напишет объявление, которое продаст её за 24 часа.
""")

st.info("💡 **Как это работает?** 1. Сделай фото ➡️ 2. Узнай цену рынка ➡️ 3. Выложи на Авито ➡️ 4. Кайфуй от свободного места и денег!")

# --- БОКОВАЯ ПАНЕЛЬ С ЛИЧНЫМ КАБИНЕТОМ ---
with st.sidebar:
    st.header("👤 Ваш ИИ-Ассистент")
    st.write("**Пользователь:** Искандер")
    st.write("**Статус тарифа:** 👑 Premium Access")
    st.markdown("---")
    st.subheader("🤖 Наш Telegram-бот")
    st.write("Хотите расхламляться без ограничений прямо с телефона и сохранять историю своих продаж?")
    st.link_button("🚀 Открыть бота в Telegram", "https://t.me")
    st.markdown("---")
    if st.button("🧹 Очистить историю"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

tab1, tab2 = st.tabs(["🖼️ Умное Расхламление & Оценка по фото", "💬 Задать вопрос ИИ (Чат)"])

# --- ВКЛАДКА 1: УМНАЯ ОЦЕНКА ---
with tab1:
    st.subheader("📸 Шаг 1. Загрузите фото предмета, от которого хотите избавиться")
    uploaded_file = st.file_uploader("Выберите изображение (фото остатков ремонта, техники, вещей)...", type=["jpg", "jpeg", "png"])
    
    st.subheader("⚙️ Шаг 2. Укажите состояние вещи")
    item_status = st.selectbox(
        "В каком состоянии предмет?",
        [
            "Новый в упаковке / Остатки в идеале", 
            "Б/у в отличном состоянии (Почти не пользовались)", 
            "Б/у в хорошем состоянии (Есть следы использования)", 
            "На запчасти / Под восстановление / Хлам"
        ]
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Товар, который принесет вам деньги', use_container_width=True)
        
        if st.button("💰 Запустить оценку рынка и расхламление"):
            system_instruction = f"""
            Ты — профессиональный ИИ-оценщик вторичного рынка (Авито, Юла) и копирайтер.
            Изучи прикрепленное изображение товара и его состояние: "{item_status}".
            
            Выдай подробный ответ строго по следующим двум блокам:
            
            📊 БЛОК 1: АНАЛИЗ СТОИМОСТИ (В РУБЛЯХ)
            - **Что это на фото:** Точное определение модели и бренда.
            - **Рыночная цена прямо сейчас:** Средняя стоимость б/у предложений в РФ.
            - **РЕКОМЕНДУЕМАЯ ВИЛКА ЦЕН:** Минимальная и максимальная цена в рублях.
            - **Вердикт:** Почему стоит продать это прямо сейчас.
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ
            - **Заголовок:** Придумай цепляющий заголовок для Авито.
            - **Текст объявления:** Напиши продающий структурированный текст.
            """
            
            try:
                with st.spinner("🕵️‍♂️ ИИ сканирует фото и проверяет цены конкурентов на Авито..."):
                    # Переводим фото в base64 текст
                    buffered = io.BytesIO()
                    image.convert("RGB").save(buffered, format="JPEG", quality=80)
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Отправляем запрос на автономный ИИ-сервер
                    response = requests.post(
                        "https://pollinations.ai",
                        json={
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": system_instruction},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}
                                    ]
                                }
                            ],
                            "model": "openai" # Безотказная большая зрительная модель
                        },
                        timeout=45
                    )
                    ai_reply = response.text
                    
                if ai_reply:
                    st.success("🤖 Рынок успешно проанализирован! Забирайте ваши деньги:")
                    st.write(ai_reply)
                else:
                    st.error("ИИ временно перегружен, попробуйте еще раз через 10 секунд.")
                    
            except Exception as e:
                st.error(f"Не удалось выполнить оценку. Ошибка: {e}")

# --- ВКЛАДКА 2: ТЕКСТОВЫЙ ЧАТ ---
with tab2:
    st.subheader("🤖 Задайте ИИ любой вопрос про продажи и расхламление")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Напишите вопрос..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        try:
            with st.spinner("ИИ пишет ответ..."):
                response = requests.post(
                    "https://pollinations.ai",
                    json={
                        "messages": [{"role": "user", "content": user_input}],
                        "model": "openai"
                    },
                    timeout=30
                )
                reply = response.text
            with st.chat_message("assistant"):
                st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Ошибка ИИ: {e}")
