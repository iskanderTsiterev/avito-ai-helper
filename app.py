import streamlit as st
import requests
from PIL import Image

# Вставляем ваш проверенный ключ напрямую в код для 100% надежности
VSEGPT_KEY = "sk-or-vis-3f438e-c4bd6a619441d28293437943779b8ed57b7488e2d6dc2e3f376691b546ed2ef2"

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
    st.write("**Статус тарифа:** 🆓 Тестовый баланс ВсеGPT")
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
            st.warning("⚠️ Пожалуйста, введите название предмета в поле выше!")
        else:
            system_instruction = f"""
            Ты — профессиональный ИИ-оценщик вторичного рынка (Авито) и копирайтер.
            Ты должен помочь пользователю Искандеру оценить предмет: "{item_title}", состояние: "{item_status}".
            
            Выдай подробный ответ строго на русском языке по следующим блокам:
            📊 БЛОК 1: АНАЛИЗ СТОИМОСТИ (Средняя б/у цена на Авито в РФ и вилка цен от минимальной до максимальной).
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ (Цепляющий заголовок и структурированный продающий текст).
            """
            
            url = "https://vsegpt.ru"
            headers = {
                "Authorization": f"Bearer {VSEGPT_KEY.strip()}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": system_instruction}]
            }
            
            try:
                with st.spinner("🕵️‍♂️ ИИ анализирует рынок вторички РФ..."):
                    response = requests.post(url, json=data, headers=headers)
                    result_json = response.json()
                
                if response.status_code == 200 and "choices" in result_json:
                    ai_text = result_json["choices"][0]["message"]["content"]
                    st.success("🤖 Рынок успешно проанализирован! Забирайте ваши деньги:")
                    st.markdown(ai_text)
                else:
                    error_msg = result_json.get("error", {}).get("message", str(result_json))
                    st.error(f"Ошибка авторизации ВсеGPT: {error_msg}")
                    
            except Exception as e:
                st.error(f"Не удалось выполнить веб-запрос: {e}")

# --- ВКЛАДКА 2: ТЕКСТОВЫЙ ЧАТ С ИИ ---
with tab2:
    st.subheader("🤖 Задайте ИИ любой вопрос про продажи и расхламление")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if user_input := st.chat_input("Напишите вопрос..."):
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        url = "https://vsegpt.ru"
        headers = {"Authorization": f"Bearer {VSEGPT_KEY.strip()}", "Content-Type": "application/json"}
        
        formatted_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        data = {"model": "openai/gpt-4o-mini", "messages": formatted_messages}
        
        try:
            with st.spinner("ИИ пишет ответ..."):
                response = requests.post(url, json=data, headers=headers)
                result_json = response.json()
                
            if response.status_code == 200 and "choices" in result_json:
                ai_response_text = result_json["choices"][0]["message"]["content"]
                with st.chat_message("assistant"):
                    st.write(ai_response_text)
                st.session_state.messages.append({"role": "assistant", "content": ai_response_text})
            else:
                st.error("Ошибка ИИ в чате. Проверьте ключ.")
        except Exception as e:
            st.error(f"Ошибка сети в чате: {e}")
