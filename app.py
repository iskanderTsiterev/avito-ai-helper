import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import io
import base64

# Инициализируем бесплатного автономного клиента без ключей
client = InferenceClient()

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
    st.write("**Статус тарифа:** 👁️ Прямое ИИ-Зрение (Безлимит)")
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
        
        # Сжимаем фото для быстрой отправки
        image.thumbnail((600, 600))
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
            user_text_hint = f"\nПодсказка пользователя: {item_title}, {item_status}." if item_title else ""
            
            system_instruction = f"""
            Ты — эксперт вторичного рынка Авито со зритетельным анализом. 
            Перед тобой реальное фото предмета. {user_text_hint}
            
            ВНИМАТЕЛЬНО ИЗУЧИ ИЗОБРАЖЕНИЕ И ОПРЕДЕЛИ ГЛАЗАМИ, ЧТО НА НЕМ НАХОДИТСЯ.
            
            Выдай ответ строго на русском языке в следующем формате:
            
            📊 БЛОК 1: ЧТО УВИДЕЛ ИИ И РЕАЛЬНАЯ СТОИМОСТЬ
            - **Результат сканирования фото:** Подробно опиши, какой именно предмет ты видишь на картинке, его цвет, бренд (если видно) и форму.
            - **Вторичный рынок РФ:** Реальная средняя б/у цена этого конкретного товара на Авито прямо сейчас.
            - **Рекомендуемая вилка цен:** Минимальная цена (чтобы забрали сегодня) и максимальная цена.
            - **Совет оценщика:** Что сделать с вещью на фото, чтобы продать её дороже.
            
            📝 БЛОК 2: ГОТОВОЕ ОБЪЯВЛЕНИЕ ДЛЯ АВИТО
            - **Заголовок:** Идеальный поисковый заголовок для Авито.
            - **Описание:** Живой продающий текст, описывающий ИМЕННО ТОТ ПРЕДМЕТ, что на фото.
            """
            
            try:
                with st.spinner("👁️ Автономный ИИ детально изучает ваше фото..."):
                    # Делаем прямой запрос в зрячую модель через официальную библиотеку
                    response = client.chat_completion(
                        model="Qwen/Qwen2.5-VL-7B-Instruct",
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
                        ],
                        max_tokens=800
                    )
                
                ai_text = response.choices[0].message.content
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
                response = client.chat_completion(
                    model="Qwen/Qwen2.5-VL-7B-Instruct",
                    messages=[{"role": "user", "content": user_input}],
                    max_tokens=300
                )
            with st.chat_message("assistant"):
                st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Ошибка чата: {e}")
