import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import base64

# Инициализируем клиента ВсеGPT через официальный адрес v1
ai_client = OpenAI(
    base_url="https://vsegpt.ru",
    api_key=st.secrets["VSEGPT_API_KEY"].strip()
)

# Настройка интерфейса сайта в браузере
st.set_page_config(page_title="Авито Расхламление с ИИ", page_icon="✨", layout="centered")

# --- ГЛАВНЫЙ БАННЕР И МАРКЕТИНГОВЫЙ ЗАГОЛОВОК ---
st.title("✨ Преврати ненужный хлам в чистые деньги!")
st.subheader("Освободи место в доме и заработай на этом с помощью ИИ")
st.markdown("""
У каждого в доме есть вещи, которые лежат без дела. **Пора превратить этот мусор в свободное пространство и рубли на карте!**

Наш зрячий искусственный интеллект мгновенно проанализирует **ваше фото**, 
выдаст точную стоимость вещи и напишет уникальное объявление.
""")

# --- БОКОВАЯ ПАНЕЛЬ С ЛИЧНЫМ КАБИНЕТОМ ---
with st.sidebar:
    st.header("👤 Ваш ИИ-Ассистент")
    st.write("**Пользователь:** Искандер")
    st.write("**Статус тарифа:** 👁️ ИИ-Зрение со сжатием фото")
    st.markdown("---")
    if st.button("🧹 Очистить историю"):
        st.session_state.messages = []
        st.rerun()

tab1, tab2 = st.tabs(["🖼️ Умное Расхламление & Оценка", "💬 Задать вопрос ИИ (Чат)"])

# --- ВКЛАДКА 1: УМНАЯ ОЦЕНКА ---
with tab1:
    st.subheader("📸 Шаг 1. Загрузите фото предмета (Основа для ИИ)")
    uploaded_file = st.file_uploader("Выберите изображение предмета...", type=["jpg", "jpeg", "png"])
    
    image_base64 = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Товар подготовлен к визуальному анализу', use_container_width=True)
        
        # МАГИЯ СЖАТИЯ: Уменьшаем картинку до 800 пикселей
        image.thumbnail((800, 800))
        
        # Конвертируем сжатую картинку в формат Base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=80)
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    st.subheader("📝 Шаг 2. Дополнительное описание (Необязательно)")
    st.markdown("*Заполните эти поля, только если ИИ не сможет распознать модель по фото или нужно указать скрытые дефекты:*")
    item_title = st.text_input("Название/дополнение (подсказка для ИИ)", placeholder="Например: Духи Versace Versense 100мл, оригинал")
    item_status = st.text_input("Состояние/нюансы (скрытые сколы, коробка)", placeholder="Например: новый, б/у, без коробки")
    
    if st.button("💰 Запустить сканирование и оценку по фото"):
        if uploaded_file is None:
            st.warning("⚠️ Пожалуйста, загрузите фотографию! Наш ИИ проводит оценку 100% на основе изображения.")
        else:
            user_text_hint = f"\nТекстовая подсказка от пользователя (модель/состояние): {item_title}, {item_status}." if item_title else ""
            
            system_instruction = f"""
            Ты — эксперт вторичного рынка Авито со встроенным компьютерным зрением. 
            Перед тобой реальное фото предмета, который пользователь хочет продать.
            {user_text_hint}
            
            ВНИМАТЕЛЬНО ИЗУЧИ ИЗОБРАЖЕНИЕ:
            1. Определи, ЧТО ИМЕННО находится на фотографии (бренд, модель, цвет, материал, количество, сфера применения).
            2. Оцени внешний вид товара, его сохранность, упаковку и видимые дефекты. Определи это исключительно глазами по картинке!
            
            Выдай подробный ответ строго на русском языке в следующем формате:
            
            📊 БЛОК 1: ЧТО УВИДЕЛ ИИ И РЕАЛЬНАЯ СТОИМОСТЬ
            - **Результат сканирования фото:** Подробно опиши, какой именно предмет ты видишь на картинке, его цвет, комплектацию, примерное количество и форму.
            - **Вторичный рынок РФ:** Реальная средняя б/у цена этого конкретного товара на Авито прямо сейчас.
            - **Рекомендуемая вилка цен:** Минимальная цена (чтобы забрали сегодня) и максимальная цена (если готовы подождать).
            - **Совет оценщика:** Что сделать с вещью на фото, чтобы продать её дороже (протереть, найти коробку, указать точные размеры).
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ БЫСТРОЙ ПРОДАЖИ
            - **Заголовок:** Идеальный поисковый заголовок для Авито.
            - **Описание:** Живой продающий текст, описывающий ИМЕННО ТОТ ПРЕДМЕТ, что на фото. Укажи параметры, которые ты заметил на картинке, причину продажи, блок доставки и призыв написать в ЛС.
            """
            
            try:
                with st.spinner("👁️ Зрячий ИИ ВсеGPT детально изучает ваше фото..."):
                    response = ai_client.chat.completions.create(
                        model="google/gemini-2.5-flash",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": system_instruction},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ]
                    )
                
                # ИСПРАВЛЕНО: Всеядная расшифровка ответа (обрабатывает и строку, и объект Choices)
                if isinstance(response, str):
                    ai_text = response
                elif hasattr(response, 'choices') and len(response.choices) > 0:
                    ai_text = response.choices.message.content
                else:
                    ai_text = str(response)

                st.success("🤖 Визуальный анализ фотографии успешно завершен!")
                st.markdown(ai_text)
                
            except Exception as e:
                st.error(f"Не удалось выполнить оценку. Ошибка сервера: {e}")

# --- ВКЛАДКА 2: ТЕКСТОВЫЙ ЧАТ С ИИ ---
with tab2:
    st.subheader("🤖 Чат-поддержка по продажам")
    if user_input := st.chat_input("Напишите ваш вопрос..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        try:
            with st.spinner("ИИ пишет ответ..."):
                response = ai_client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role": "user", "content": user_input}]
                )
            
            if isinstance(response, str):
                chat_text = response
            elif hasattr(response, 'choices') and len(response.choices) > 0:
                chat_text = response.choices.message.content
            else:
                chat_text = str(response)

            with st.chat_message("assistant"):
                st.markdown(chat_text)
        except Exception as e:
            st.error(f"Ошибка чата: {e}")
