import streamlit as st
from openai import OpenAI
from PIL import Image

# Безопасно инициализируем клиента через ВсеGPT
ai_client = OpenAI(
    base_url="https://vsegpt.ru",
    api_key=st.secrets["VSEGPT_API_KEY"]
)

# Настройка интерфейса сайта в браузере
st.set_page_config(page_title="Авито Расхламление с ИИ", page_icon="✨", layout="centered")

# --- ГЛАВНЫЙ БАННЕР И МАРКЕТИНГОВЫЙ ЗАГОЛОВОК ---
st.title("✨ Преврати ненужный хлам в чистые деньги!")
st.subheader("Освободи место в доме и заработай на этом с помощью ИИ")
st.markdown("""
У каждого в доме есть вещи, которые лежат без дела. **Пора превратить этот мусор в свободное пространство и рубли на карте!**

Наш искусственный интеллект мгновенно проанализирует рынок вторички РФ, 
выдаст точную стоимость вещи и напишет объявление, которое продаст её за 24 часа.
""")

st.info("💡 **Как это работает?** 1. Сделай фото ➡️ 2. Напиши название ➡️ 3. Узнай цену рынка ➡️ 4. Выложи на Авито!")

# --- БОКОВАЯ ПАНЕЛЬ С ЛИЧНЫМ КАБИНЕТОМ ---
with st.sidebar:
    st.header("👤 Ваш ИИ-Ассистент")
    st.write("**Пользователь:** Искандер")
    st.write("**Статус тарифа:** 🆓 Бесплатный безлимит РФ")
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

tab1, tab2 = st.tabs(["🖼️ Умное Расхламление & Оценка", "💬 Задать вопрос ИИ (Чат)"])

# --- ВКЛАДКА 1: УМНАЯ ОЦЕНКА ---
with tab1:
    st.subheader("📸 Шаг 1. Загрузите фото предмета (для наглядности)")
    uploaded_file = st.file_uploader("Выберите изображение предмета...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Ваш товар подготовлен к оценке', use_container_width=True)
    
    st.subheader("📝 Шаг 2. Напишите, что это за вещь и её состояние")
    item_title = st.text_input("Например: Духи Versace Versense 100мл, оригинал", placeholder="Введите название предмета...")
    
    item_status = st.selectbox(
        "В каком состоянии предмет?",
        [
            "Новый в упаковке / Идеальное состояние", 
            "Б/у в отличном состоянии (Почти не пользовались)", 
            "Б/у в хорошем состоянии (Есть следы использования)", 
            "На запчасти / Хлам"
        ]
    )
    
    if st.button("💰 Запустить оценку рынка и расхламление"):
        if not item_title:
            st.warning("⚠️ Пожалуйста, введите название предмета в поле выше, чтобы ИИ смог найти его на рынке!")
        else:
            system_instruction = f"""
            Ты — профессиональный ИИ-оценщик вторичного рынка (Авито) и копирайтер.
            Твоя цель — помочь пользователю Искандеру расхламить дом, избавиться от ненужной вещи и заработать на этом.
            
            Предмет для анализа: "{item_title}"
            Состояние предмета: "{item_status}"
            
            Выдай подробный ответ строго на русском языке по следующим блокам:
            
            📊 БЛОК 1: АНАЛИЗ СТОИМОСТИ (СКОЛЬКО ДЕНЕГ ВЫ ПОЛУЧИТЕ)
            - **Что оцениваем:** Подробное описание модели, бренда и характеристик на основе введенного текста.
            - **Рыночная цена прямо сейчас:** Средняя стоимость аналогичных б/у предложений на Авито/Юле в РФ.
            - **РЕКОМЕНДУЕМАЯ ВИЛКА ЦЕН:** Назови минимальную цену (чтобы забрали сегодня) и максимальную цену (если готовы подождать неделю).
            - **Вердикт оценщика:** Почему стоит продать это прямо сейчас.
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ
            - **Заголовок:** Придумай цепляющий, оптимизированный под поиск заголовок на Авито.
            - **Текст объявления:** Напиши структурированный, честный и продающий текст. Укажи параметры, причину продажи ("освобождаю место"), блок доставки и призыв написать в личку.
            """
            try:
                with st.spinner("🕵️‍♂️ ИИ мгновенно анализирует рынок вторички РФ..."):
                    response = ai_client.chat.completions.create(
                        model="meta-llama/llama-3.1-8b-instruct:free",
                        messages=[
                            {"role": "user", "content": system_instruction}
                        ]
                    )
                st.success("🤖 Рынок успешно проанализирован! Забирайте ваши деньги:")
                
                # Извлекаем текст
                if isinstance(response, str):
                    ai_text = response
                else:
                    ai_text = response.choices.message.content
                    
                st.markdown(ai_text)
                
                st.markdown("---")
                st.info("💡 **Понравился результат?** Забирай безлимитный доступ к оценщику в нашем Telegram-боте!")
                st.link_button("💬 Перейти в Telegram-бот", "https://t.me")
            except Exception as e:
                st.error(f"Не удалось выполнить оценку. Ошибка сервера: {e}")

# --- ВКЛАДКА 2: ТЕКСТОВЫЙ ЧАТ С ИИ ---
with tab2:
    st.subheader("🤖 Задайте ИИ любой вопрос про продажи и расхламление")
    st.write("Например: *'Как правильно общаться с покупателями на Авито?'* или *'За сколько можно продать старый сломанный холодильник?'*")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Напишите вопрос..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        formatted_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        try:
            with st.spinner("ИИ пишет ответ..."):
                response = ai_client.chat.completions.create(
                    model="meta-llama/llama-3.1-8b-instruct:free",
                    messages=formatted_messages
                )
            
            if isinstance(response, str):
                ai_response_text = response
            else:
                ai_response_text = response.choices.message.content
            
            with st.chat_message("assistant"):
                st.write(ai_response_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
        except Exception as e:
            st.error(f"Ошибка ИИ в чате: {e}")
