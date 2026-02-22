from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Записаться на занятие", callback_data="book_lesson")
    kb.button(text="📋 Мои записи", callback_data="my_bookings")
    kb.button(text="ℹ️ О тренере", callback_data="about_trainer")
    kb.button(text="📞 Контакты", callback_data="contacts")
    kb.adjust(1, 2, 1)
    
    # Применяем цвета к кнопкам
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "book_lesson":
                button.style = "primary"
            elif button.callback_data == "my_bookings":
                button.style = "success"
    
    return markup

def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить занятие", callback_data="admin_add_lesson")
    kb.button(text="📋 Все занятия", callback_data="admin_lessons")
    kb.button(text="👥 Все записи", callback_data="admin_bookings")
    kb.button(text="📢 Рассылка", callback_data="admin_broadcast")
    kb.button(text="👤 Пользователи", callback_data="admin_users")
    kb.button(text="◀️ Назад", callback_data="back_to_main")
    kb.adjust(1, 2, 2, 1)
    
    # Применяем цвета
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "admin_add_lesson":
                button.style = "success"
            elif button.callback_data == "admin_broadcast":
                button.style = "primary"
    
    return markup

def gender_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="👨 Мужской", callback_data="gender_m")
    kb.button(text="👩 Женский", callback_data="gender_f")
    kb.adjust(2)
    return kb.as_markup()

def back_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Назад", callback_data="back_to_main")
    return kb.as_markup()

def cancel_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="❌ Отмена", callback_data="cancel")
    
    # Применяем цвет
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel":
                button.style = "danger"
    
    return markup

def lessons_keyboard(lessons, page=0):
    """Клавиатура с доступными занятиями для пользователей с пагинацией"""
    kb = InlineKeyboardBuilder()
    
    # Пагинация: 6 занятий на страницу
    items_per_page = 6
    start = page * items_per_page
    end = start + items_per_page
    total_pages = (len(lessons) + items_per_page - 1) // items_per_page
    
    page_lessons = lessons[start:end]
    
    for lesson in page_lessons:
        lesson_id, date, time, duration, price, description, is_available, _ = lesson
        kb.button(
            text=f"{date} в {time} - {price}₽",
            callback_data=f"lesson_{lesson_id}"
        )
    
    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(("◀️", f"lessons_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(("▶️", f"lessons_page_{page+1}"))
    
    for text, callback in nav_buttons:
        kb.button(text=text, callback_data=callback)
    
    kb.button(text="🏠 В меню", callback_data="back_to_main")
    
    # Расположение: 2-1-2-1
    lesson_count = len(page_lessons)
    nav_count = len(nav_buttons)
    
    if lesson_count == 1:
        kb.adjust(1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 2:
        kb.adjust(2, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 3:
        kb.adjust(2, 1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 4:
        kb.adjust(2, 1, 1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 5:
        kb.adjust(2, 1, 2, nav_count if nav_count > 0 else 1, 1)
    else:  # 6
        kb.adjust(2, 1, 2, 1, nav_count if nav_count > 0 else 1, 1)
    
    return kb.as_markup()

def confirm_booking(lesson_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"confirm_book_{lesson_id}")
    kb.button(text="❌ Отмена", callback_data="back_to_main")
    kb.adjust(2)
    
    # Применяем цвета
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("confirm_book_"):
                button.style = "success"
            elif button.callback_data == "back_to_main":
                button.style = "danger"
    
    return markup

def admin_lessons_keyboard(lessons, page=0):
    """Клавиатура со списком занятий для админа с пагинацией"""
    kb = InlineKeyboardBuilder()
    
    # Пагинация: 6 занятий на страницу
    items_per_page = 6
    start = page * items_per_page
    end = start + items_per_page
    total_pages = (len(lessons) + items_per_page - 1) // items_per_page
    
    page_lessons = lessons[start:end]
    
    for lesson in page_lessons:
        lesson_id, date, time, duration, price, description, is_available, _ = lesson
        status = "✅" if is_available else "❌"
        kb.button(
            text=f"{status} {date} {time} - {price}₽",
            callback_data=f"admin_lesson_{lesson_id}"
        )
    
    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(("◀️", f"admin_lessons_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(("▶️", f"admin_lessons_page_{page+1}"))
    
    for text, callback in nav_buttons:
        kb.button(text=text, callback_data=callback)
    
    kb.button(text="🏠 В меню", callback_data="back_to_admin")
    
    # Расположение: 2-1-2-1 для занятий, потом навигация
    lesson_count = len(page_lessons)
    nav_count = len(nav_buttons)
    
    if lesson_count == 1:
        kb.adjust(1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 2:
        kb.adjust(2, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 3:
        kb.adjust(2, 1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 4:
        kb.adjust(2, 1, 1, nav_count if nav_count > 0 else 1, 1)
    elif lesson_count == 5:
        kb.adjust(2, 1, 2, nav_count if nav_count > 0 else 1, 1)
    else:  # 6
        kb.adjust(2, 1, 2, 1, nav_count if nav_count > 0 else 1, 1)
    
    return kb.as_markup()

def admin_users_keyboard(users, page=0):
    """Клавиатура со списком пользователей с пагинацией"""
    kb = InlineKeyboardBuilder()
    
    # Пагинация: 6 пользователей на страницу
    items_per_page = 6
    start = page * items_per_page
    end = start + items_per_page
    total_pages = (len(users) + items_per_page - 1) // items_per_page
    
    page_users = users[start:end]
    
    for user in page_users:
        user_id, first_name, last_name, phone, gender, age, _ = user
        kb.button(
            text=f"{first_name} {last_name} ({age} лет)",
            callback_data=f"admin_user_{user_id}"
        )
    
    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(("◀️", f"admin_users_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(("▶️", f"admin_users_page_{page+1}"))
    
    # Добавляем навигацию
    for text, callback in nav_buttons:
        kb.button(text=text, callback_data=callback)
    
    kb.button(text="🔍 Поиск", callback_data="admin_user_search")
    kb.button(text="🏠 В меню", callback_data="back_to_admin")
    
    # Расположение: 2-1-2-1 для пользователей, потом навигация и кнопки
    user_count = len(page_users)
    nav_count = len(nav_buttons)
    
    if user_count == 1:
        kb.adjust(1, nav_count if nav_count > 0 else 1, 1, 1)
    elif user_count == 2:
        kb.adjust(2, nav_count if nav_count > 0 else 1, 1, 1)
    elif user_count == 3:
        kb.adjust(2, 1, nav_count if nav_count > 0 else 1, 1, 1)
    elif user_count == 4:
        kb.adjust(2, 1, 1, nav_count if nav_count > 0 else 1, 1, 1)
    elif user_count == 5:
        kb.adjust(2, 1, 2, nav_count if nav_count > 0 else 1, 1, 1)
    else:  # 6
        kb.adjust(2, 1, 2, 1, nav_count if nav_count > 0 else 1, 1, 1)
    
    return kb.as_markup()

def admin_user_detail_keyboard(user_id):
    """Клавиатура для профиля пользователя"""
    kb = InlineKeyboardBuilder()
    kb.button(text="📋 История занятий", callback_data=f"admin_user_history_{user_id}")
    kb.button(text="◀️ К списку", callback_data="admin_users")
    kb.adjust(1)
    return kb.as_markup()

def admin_bookings_keyboard(bookings, page=0):
    """Клавиатура со списком записей с пагинацией"""
    kb = InlineKeyboardBuilder()
    
    # Пагинация: 6 записей на страницу
    items_per_page = 6
    start = page * items_per_page
    end = start + items_per_page
    total_pages = (len(bookings) + items_per_page - 1) // items_per_page
    
    page_bookings = bookings[start:end]
    
    for booking in page_bookings:
        booking_id, first_name, last_name, phone, date, time, price, status = booking
        kb.button(
            text=f"{first_name} {last_name} - {date}",
            callback_data=f"admin_booking_{booking_id}"
        )
    
    # Кнопки пагинации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(("◀️", f"admin_bookings_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(("▶️", f"admin_bookings_page_{page+1}"))
    
    for text, callback in nav_buttons:
        kb.button(text=text, callback_data=callback)
    
    kb.button(text="🏠 В меню", callback_data="back_to_admin")
    
    # Расположение: 2-1-2-1
    booking_count = len(page_bookings)
    nav_count = len(nav_buttons)
    
    if booking_count == 1:
        kb.adjust(1, nav_count if nav_count > 0 else 1, 1)
    elif booking_count == 2:
        kb.adjust(2, nav_count if nav_count > 0 else 1, 1)
    elif booking_count == 3:
        kb.adjust(2, 1, nav_count if nav_count > 0 else 1, 1)
    elif booking_count == 4:
        kb.adjust(2, 1, 1, nav_count if nav_count > 0 else 1, 1)
    elif booking_count == 5:
        kb.adjust(2, 1, 2, nav_count if nav_count > 0 else 1, 1)
    else:  # 6
        kb.adjust(2, 1, 2, 1, nav_count if nav_count > 0 else 1, 1)
    
    return kb.as_markup()

def date_quick_select():
    """Быстрый выбор даты"""
    from datetime import datetime, timedelta
    kb = InlineKeyboardBuilder()
    
    # Русские названия дней недели
    weekdays_ru = {
        0: "Пн",
        1: "Вт", 
        2: "Ср",
        3: "Чт",
        4: "Пт",
        5: "Сб",
        6: "Вс"
    }
    
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        if i == 0:
            day_name = "Сегодня"
        elif i == 1:
            day_name = "Завтра"
        elif i == 2:
            day_name = "Послезавтра"
        else:
            day_name = weekdays_ru[date.weekday()]
        
        date_str = date.strftime("%d.%m.%Y")
        kb.button(text=f"{day_name} ({date.strftime('%d.%m')})", callback_data=f"date_{date_str}")
    
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    
    # Расположение: 2-1-2-1-1 + отмена
    kb.adjust(2, 1, 2, 1, 1, 1)
    
    markup = kb.as_markup()
    # Безопасное применение стиля
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def time_quick_select():
    """Быстрый выбор времени"""
    kb = InlineKeyboardBuilder()
    
    # Время с 9:00 до 22:00 с шагом в час
    times = []
    for hour in range(9, 23):
        times.append(f"{hour:02d}:00")
    
    for time in times:
        kb.button(text=time, callback_data=f"time_{time}")
    
    kb.button(text="⏰ Свое время", callback_data="time_manual")
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    
    # Расположение: 2-1-2-1-2-1-2-1-2-1-2-1 + 2 кнопки внизу
    # Всего 14 кнопок времени + 2 кнопки = 16
    kb.adjust(2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2)
    
    # Применяем цвет к кнопке отмены
    markup = kb.as_markup()
    # Находим кнопку отмены и применяем стиль
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def duration_quick_select():
    """Быстрый выбор длительности"""
    kb = InlineKeyboardBuilder()
    
    durations = [
        ("30 мин", 30),
        ("45 мин", 45),
        ("1 час", 60),
        ("1.5 часа", 90),
        ("2 часа", 120),
        ("3 часа", 180)
    ]
    
    for text, minutes in durations:
        kb.button(text=text, callback_data=f"duration_{minutes}")
    
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    
    # Расположение: 2-1-2-1 + отмена
    kb.adjust(2, 1, 2, 1, 1)
    
    markup = kb.as_markup()
    # Безопасное применение стиля
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def price_quick_select():
    """Быстрый выбор цены"""
    kb = InlineKeyboardBuilder()
    
    prices = [500, 700, 1000, 1200, 1500, 2000, 2500, 3000]
    
    for price in prices:
        kb.button(text=f"{price}₽", callback_data=f"price_{price}")
    
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    
    # Расположение: 2-1-2-1-2 + отмена
    kb.adjust(2, 1, 2, 1, 2, 1)
    
    markup = kb.as_markup()
    # Безопасное применение стиля
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def description_quick_select():
    """Быстрый выбор описания"""
    kb = InlineKeyboardBuilder()
    
    descriptions = [
        ("🎯 Базовая техника", "Обучение базовой технике удара и постановке"),
        ("🏆 Продвинутый уровень", "Тактика игры и сложные удары"),
        ("👥 Групповое занятие", "Групповое занятие (2-3 человека)"),
        ("🎓 Первое занятие", "Первое пробное занятие"),
        ("⚡ Интенсив", "Интенсивная тренировка"),
    ]
    
    for text, desc in descriptions:
        kb.button(text=text, callback_data=f"desc_{descriptions.index((text, desc))}")
    
    kb.button(text="⏭ Пропустить", callback_data="desc_skip")
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    
    # Расположение: 2-1-2 + кнопки
    kb.adjust(2, 1, 2, 2)
    
    markup = kb.as_markup()
    # Безопасное применение стиля
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def broadcast_quick_templates():
    """Шаблоны для рассылки"""
    kb = InlineKeyboardBuilder()
    
    kb.button(text="🆓 Освободилось место", callback_data="broadcast_template_free")
    kb.button(text="📅 Новые занятия", callback_data="broadcast_template_new")
    kb.button(text="🎉 Акция/Скидка", callback_data="broadcast_template_promo")
    kb.button(text="⏰ Напоминание", callback_data="broadcast_template_reminder")
    kb.button(text="ℹ️ Информация", callback_data="broadcast_template_info")
    kb.button(text="✏️ Свое сообщение", callback_data="broadcast_custom")
    kb.button(text="❌ Отмена", callback_data="cancel_admin")
    kb.adjust(2, 2, 1, 1, 1)
    
    # Применяем цвета
    markup = kb.as_markup()
    # Безопасное применение стилей
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data == "broadcast_template_free":
                button.style = "success"
            elif button.callback_data == "broadcast_template_promo":
                button.style = "primary"
            elif button.callback_data == "cancel_admin":
                button.style = "danger"
    
    return markup

def confirm_delete(lesson_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}")
    kb.button(text="❌ Отмена", callback_data="admin_lessons")
    kb.adjust(2)
    
    # Применяем цвета
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("confirm_delete_"):
                button.style = "danger"
    
    return markup


def admin_lesson_detail_keyboard(lesson_id):
    """Клавиатура для управления конкретным занятием"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Удалить занятие", callback_data=f"admin_delete_{lesson_id}")
    kb.button(text="◀️ Назад к списку", callback_data="admin_lessons")
    kb.adjust(1)
    
    # Применяем цвет
    markup = kb.as_markup()
    for row in markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith("admin_delete_"):
                button.style = "danger"
    
    return markup
