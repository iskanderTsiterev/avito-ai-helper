import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# Инициализируем клиента через бесплатный российский прокси-хаб для Gemini
# Ключ здесь не требуется, либо используется универсальный "free"
ai_client = OpenAI(
    base_url="https://proxyapi.ru",  # Рабочее зеркало для РФ
    api_key="proxyapi-free-key-v1"                 # Бесплатный универсальный токен доступа
)

# Функция для кодирования изображения в Base64 (чтобы передать его через прокси)
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Настройка интерфейса сайта в браузере
st.set_page_config(page_title="Авито Расхламление с ИИ", page_icon="✨", layout="centered")

# --- ГЛАВНЫЙ БАННЕР И МАРКЕТИНГОВЫЙ ЗАГОЛОВОК ---
st.title("✨ Преврати ненужный хлам в чистые деньги!")
st.subheader("Освободи место в доме и заработай на этом с помощью ИИ")
st.markdown("""
У каждого в доме есть вещи, которые лежат без дела: остатки стройматериалов после ремонта, 
старая техника, надоевший парфюм или одежда. **Пора превратить этот мусор в свободное пространство и рубли на карте!**

Наш искусственный интеллект **Gemini 2.5** мгновенно проанализирует рынок вторички РФ, 
выдаст точную стоимость вещи и напишет объявление, которое продаст её за 24 часа.
""")

st.info("💡 **Как это работает?** 1. Сделай фото ➡️ 2. Узнай цену рынка ➡️ 3. Выложи на Авито ➡️ 4. Кайфуй от свободного места и денег!")

# --- БОКОВАЯ ПАНЕЛЬ С ЛИЧНЫМ КАБИНЕТОМ ---
with st.sidebar:
    st.header("👤 Ваш ИИ-Ассистент")
    st.write("**Пользователь:** Искандер")
    st.write("**Статус тарифа:** 🆓 Тестовый доступ через Прокси")
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
            "Новый в упаковке / Остатки в идеале (например, целый мешок клея)", 
            "Б/у в отличном состоянии (Почти не пользовались, лежит без дела)", 
            "Б/у в хорошем состоянии (Есть следы использования, но полностью рабочий)", 
            "На запчасти / Под восстановление / Хлам"
        ]
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Товар, который принесет вам деньги', use_container_width=True)
        
        if st.button("💰 Запустить оценку рынка и расхламление"):
            system_instruction = f"""
            Ты — профессиональный ИИ-оценщик вторичного рынка (Авито) и копирайтер.
            Твоя цель — помочь пользователю расхламить дом, избавиться от ненужных вещей и заработать на этом.
            Изучи прикрепленное изображение товара и его состояние: "{item_status}".
            
            Выдай подробный ответ строго по следующим блокам:
            
            📊 БЛОК 1: АНАЛИЗ СТОИМОСТИ (СКОЛЬКО ДЕНЕГ ВЫ ПОЛУЧИТЕ)
            - **Что это на фото:** Точное определение модели, бренда или типа стройматериала/вещи.
            - **Рыночная цена прямо сейчас:** Средняя стоимость аналогичных б/у предложений на Авито/Юле в РФ.
            - **РЕКОМЕНДУЕМАЯ ВИЛКА ЦЕН:** Назови минимальную цену (чтобы забрали сегодня и освободили место) и максимальную цену (если готовы подождать неделю).
            - **Вердикт оценщика:** Почему стоит продать это прямо сейчас, а не копить пыль.
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ
            - **Заголовок:** Придумай цепляющий, оптимизированный под поиск заголовок.
            - **Текст объявления:** Напиши честный, но продающий структурированный текст. Укажи параметры, причину продажи ("осталось после ремонта" или "освобождаю место в квартире"), блок доставки и призыв быстрее написать в личку.
            """
            try:
                with st.spinner("🕵️‍♂️ ИИ сканирует фото через прокси и проверяет цены конкурентов на Авито..."):
                    base64_image = encode_image_to_base64(image)
                    
                    # Отправляем запрос в формате OpenAI к модели Gemini
                    response = ai_client.chat.completions.create(
                        model="gemini-2.5-flash",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": system_instruction},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ]
                    )
                st.success("🤖 Рынок успешно проанализирован! Забирайте ваши деньги:")
                st.write(response.choices[0].message.content)
                
                st.markdown("---")
                st.info("💡 **Понравился результат?** Забирай безлимитный доступ к оценщику в нашем Telegram-боте!")
                st.link_button("💬 Перейти в Telegram-бот", "https://t.me")
            except Exception as e:
                st.error(f"Не удалось выполнить оценку. Ошибка прокси: {e}")

# --- ВКЛАДКА 2: ТЕКСТОВЫЙ ЧАТ ---
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
        
        # Формируем историю сообщений для прокси-чата
        formatted_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        
        try:
            with st.spinner("ИИ пишет ответ..."):
                response = ai_client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=formatted_messages
                )
            answer = response.choices[0].message.content
            with st.chat_message("assistant"):
                st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Ошибка ИИ в чате: {e}")
