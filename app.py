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
            - **Рыночная цена прямо сейчас:** Средняя стоимость аналогичных б/у предложений в РФ.
            - **РЕКОМЕНДУЕМАЯ ВИЛКА ЦЕН:** Назови минимальную цену (чтобы забрали сегодня) и максимальную цену (если готовы подождать неделю) для Авито в рублях.
            - **Вердикт:** Почему стоит продать это прямо сейчас.
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ
            - **Заголовок:** Придумай цепляющий заголовок для Авито.
            - **Текст объявления:** Напиши продающий структурированный текст.
            """
            
            try:
                with st.spinner("🕵️‍♂️ ИИ сканирует фото и проверяет цены конкурентов на Авито..."):
                    # Оптимизируем размер изображения для моментальной передачи без перегрузок
                    buffered = io.BytesIO()
                    image.convert("RGB").save(buffered, format="JPEG", quality=60)
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Отправляем на выделенный скоростной vision-сервер Llama
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
                            "model": "llama" # Переключили на скоростную модель со зрением
                        },
                        timeout=45
                    )
                    ai_reply = response.text
                    
                if ai_reply:
                    st.success("🤖 Рынок успешно проанализирован! Забирайте ваши деньги:")
                    st.write(ai_reply)
                    
                    st.markdown("---")
                    st.info("💡 **Понравился результат?** Забирай безлимитный доступ к оценщику в нашем Telegram-боте!")
                    st.link_button("💬 Перейти в Telegram-бот", "https://t.me")
                else:
                    st.error("ИИ взял паузу, нажмите кнопку еще раз.")
                    
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
