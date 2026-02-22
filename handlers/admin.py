from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import (
    add_lesson, get_available_lessons, get_lesson, 
    update_lesson, delete_lesson, get_all_users, get_all_bookings,
    get_user, get_user_bookings
)
from keyboards import (
    admin_menu, back_button, cancel_button,
    date_quick_select, time_quick_select, duration_quick_select, 
    price_quick_select, description_quick_select, broadcast_quick_templates,
    admin_lessons_keyboard, admin_lesson_detail_keyboard, admin_users_keyboard,
    admin_user_detail_keyboard, admin_bookings_keyboard
)

router = Router()

class AddLesson(StatesGroup):
    date = State()
    time = State()
    duration = State()
    price = State()
    description = State()

class Broadcast(StatesGroup):
    message = State()

# Шаблоны описаний
DESCRIPTION_TEMPLATES = [
    "Обучение базовой технике удара и постановке",
    "Тактика игры и сложные удары",
    "Групповое занятие (2-3 человека)",
    "Первое пробное занятие",
    "Интенсивная тренировка"
]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command('admin'))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели", parse_mode="HTML")
        return
    
    await message.answer(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Админ-панель DoubleKiss</b>\n\n'
        '<blockquote><i>Управление занятиями, записями и рассылками</i></blockquote>',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == 'admin_add_lesson')
async def start_add_lesson(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление нового занятия</b>\n\n'
        '📅 <b>Выберите дату занятия:</b>',
        reply_markup=date_quick_select(),
        parse_mode="HTML"
    )
    await state.set_state(AddLesson.date)
    await callback.answer()

# Обработка выбора даты
@router.callback_query(AddLesson.date, F.data.startswith('date_'))
async def process_date_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "date_manual":
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
            '📅 <b>Введите дату вручную (формат: ДД.ММ.ГГГГ):</b>',
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    date = callback.data.split('_', 1)[1]
    await state.update_data(date=date, bot_message=callback.message)
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
        f'✅ <b>Дата:</b> <code>{date}</code>\n\n'
        f'🕐 <b>Выберите время занятия:</b>'
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=time_quick_select(),
        parse_mode="HTML"
    )
    await state.set_state(AddLesson.time)
    await callback.answer()

# Обработка выбора времени
@router.callback_query(AddLesson.time, F.data.startswith('time_'))
async def process_time_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "time_manual":
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
            '🕐 <b>Введите время вручную</b>\n\n'
            '<blockquote><i>Например: 14:30 или 09:00</i></blockquote>',
            reply_markup=cancel_button(),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    time = callback.data.split('_', 1)[1]
    await state.update_data(time=time)
    
    data = await state.get_data()
    
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
        f'✅ <b>Дата:</b> <code>{data["date"]}</code>\n'
        f'✅ <b>Время:</b> <code>{time}</code>\n\n'
        f'⏱ <b>Выберите длительность:</b>',
        reply_markup=duration_quick_select(),
        parse_mode="HTML"
    )
    await state.set_state(AddLesson.duration)
    await callback.answer()

# Обработка выбора длительности
@router.callback_query(AddLesson.duration, F.data.startswith('duration_'))
async def process_duration_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "duration_manual":
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
            '⏱ <b>Введите длительность в минутах:</b>',
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    duration = int(callback.data.split('_')[1])
    await state.update_data(duration=duration)
    
    data = await state.get_data()
    
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
        f'✅ <b>Дата:</b> <code>{data["date"]}</code>\n'
        f'✅ <b>Время:</b> <code>{data["time"]}</code>\n'
        f'✅ <b>Длительность:</b> {duration} мин\n\n'
        f'💰 <b>Выберите стоимость:</b>',
        reply_markup=price_quick_select(),
        parse_mode="HTML"
    )
    await state.set_state(AddLesson.price)
    await callback.answer()

# Обработка выбора цены
@router.callback_query(AddLesson.price, F.data.startswith('price_'))
async def process_price_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "price_manual":
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
            '💰 <b>Введите стоимость в рублях:</b>',
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    price = int(callback.data.split('_')[1])
    await state.update_data(price=price)
    
    data = await state.get_data()
    
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
        f'✅ <b>Дата:</b> <code>{data["date"]}</code>\n'
        f'✅ <b>Время:</b> <code>{data["time"]}</code>\n'
        f'✅ <b>Длительность:</b> {data["duration"]} мин\n'
        f'✅ <b>Стоимость:</b> {price}₽\n\n'
        f'📝 <b>Выберите описание:</b>',
        reply_markup=description_quick_select(),
        parse_mode="HTML"
    )
    await state.set_state(AddLesson.description)
    await callback.answer()

# Обработка выбора описания
@router.callback_query(AddLesson.description, F.data.startswith('desc_'))
async def process_description_select(callback: CallbackQuery, state: FSMContext):
    if callback.data == "desc_manual":
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Добавление занятия</b>\n\n'
            '📝 <b>Введите описание занятия:</b>',
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    if callback.data == "desc_skip":
        description = None
    else:
        desc_index = int(callback.data.split('_')[1])
        description = DESCRIPTION_TEMPLATES[desc_index]
    
    data = await state.get_data()
    
    lesson_id = await add_lesson(
        data['date'],
        data['time'],
        data['duration'],
        data['price'],
        description
    )
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Занятие успешно добавлено!</b>\n\n'
        f'📅 <b>Дата:</b> <code>{data["date"]}</code>\n'
        f'🕐 <b>Время:</b> <code>{data["time"]}</code>\n'
        f'⏱ <b>Длительность:</b> {data["duration"]} мин\n'
        f'💰 <b>Стоимость:</b> {data["price"]}₽\n'
    )
    
    if description:
        text += f'📝 <b>Описание:</b> {description}\n'
    
    await callback.message.edit_text(text, reply_markup=admin_menu(), parse_mode="HTML")
    await state.clear()
    await callback.answer("✅ Занятие добавлено!")

# Отмена действия
@router.callback_query(F.data == 'cancel_admin')
async def cancel_admin_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Действие отменено</b>',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == 'admin_lessons')
async def show_admin_lessons(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    lessons = await get_available_lessons()
    
    if not lessons:
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все занятия</b>\n\n'
            '<blockquote><i>Нет доступных занятий</i></blockquote>',
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
    else:
        text = (
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все занятия</b>\n\n'
            '<blockquote><i>Выберите занятие для управления</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=admin_lessons_keyboard(lessons, 0), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data.startswith('admin_lessons_page_'))
async def show_admin_lessons_page(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.split('_')[3])
    lessons = await get_available_lessons()
    
    text = (
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все занятия</b>\n\n'
        '<blockquote><i>Выберите занятие для управления</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=admin_lessons_keyboard(lessons, page), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('admin_lesson_'))
async def show_lesson_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    lesson_id = int(callback.data.split('_')[2])
    lesson = await get_lesson(lesson_id)
    
    if not lesson:
        await callback.answer("❌ Занятие не найдено", show_alert=True)
        return
    
    _, date, time, duration, price, description, is_available, _ = lesson
    status = "Доступно" if is_available else "Забронировано"
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Занятие #{lesson_id}</b>\n\n'
        f'<b>Дата:</b> <code>{date}</code>\n'
        f'<b>Время:</b> <code>{time}</code>\n'
        f'<b>Длительность:</b> {duration} минут\n'
        f'<b>Стоимость:</b> {price}₽\n'
        f'<b>Статус:</b> {status}\n'
    )
    
    if description:
        text += f'\n<blockquote><i>{description}</i></blockquote>'
    
    await callback.message.edit_text(text, reply_markup=admin_lesson_detail_keyboard(lesson_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'back_to_admin')
async def back_to_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Админ-панель DoubleKiss</b>\n\n'
        '<blockquote><i>Управление занятиями, записями и рассылками</i></blockquote>',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == 'admin_bookings')
async def show_admin_bookings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    bookings = await get_all_bookings()
    
    if not bookings:
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все записи</b>\n\n'
            '<blockquote><i>Нет записей</i></blockquote>',
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
    else:
        text = (
            f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все записи</b>\n\n'
            f'<b>Всего записей:</b> {len(bookings)}\n\n'
            f'<blockquote><i>Выберите запись для просмотра деталей</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=admin_bookings_keyboard(bookings, 0), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data.startswith('admin_bookings_page_'))
async def show_admin_bookings_page(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.split('_')[3])
    bookings = await get_all_bookings()
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все записи</b>\n\n'
        f'<b>Всего записей:</b> {len(bookings)}\n\n'
        f'<blockquote><i>Выберите запись для просмотра деталей</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=admin_bookings_keyboard(bookings, page), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'admin_users')
async def show_admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    users = await get_all_users()
    
    if not users:
        await callback.message.edit_text(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Пользователи бота</b>\n\n'
            '<blockquote><i>Нет пользователей</i></blockquote>',
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
    else:
        text = (
            f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Пользователи бота</b>\n\n'
            f'<b>Всего пользователей:</b> {len(users)}\n\n'
            f'<blockquote><i>Выберите пользователя для просмотра профиля</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=admin_users_keyboard(users, 0), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data.startswith('admin_users_page_'))
async def show_admin_users_page(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    page = int(callback.data.split('_')[3])
    users = await get_all_users()
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Пользователи бота</b>\n\n'
        f'<b>Всего пользователей:</b> {len(users)}\n\n'
        f'<blockquote><i>Выберите пользователя для просмотра профиля</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=admin_users_keyboard(users, page), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('admin_user_history_'))
async def show_user_history(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    user_id = int(callback.data.split('_')[3])
    user = await get_user(user_id)
    bookings = await get_user_bookings(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найдено", show_alert=True)
        return
    
    _, first_name, last_name, _, _, _, _ = user
    
    text = f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>История занятий</b>\n\n<b>{first_name} {last_name}</b>\n\n'
    
    if not bookings:
        text += '<blockquote><i>Нет записей на занятия</i></blockquote>'
    else:
        for booking in bookings:
            _, date, time, duration, price, description, status = booking
            status_text = "Подтверждено" if status == "confirmed" else "Ожидание"
            text += (
                f'<b>{date}</b> в <code>{time}</code>\n'
                f'· Длительность: {duration} мин\n'
                f'· Стоимость: {price}₽\n'
                f'· Статус: {status_text}\n\n'
            )
    
    await callback.message.edit_text(text, reply_markup=admin_user_detail_keyboard(user_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('admin_user_'))
async def show_user_profile(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    # Пропускаем если это история или поиск
    if callback.data.startswith('admin_user_history_') or callback.data.startswith('admin_user_search'):
        return
    
    user_id = int(callback.data.split('_')[2])
    user = await get_user(user_id)
    
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    _, first_name, last_name, phone, gender, age, registered_at = user
    
    # Получаем количество записей пользователя
    bookings = await get_user_bookings(user_id)
    bookings_count = len(bookings)
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Профиль пользователя</b>\n\n'
        f'<b>{first_name} {last_name}</b>\n\n'
        f'<b>Телефон:</b> <code>{phone}</code>\n'
        f'<b>Пол:</b> {gender}\n'
        f'<b>Возраст:</b> {age} лет\n'
        f'<b>Всего занятий:</b> {bookings_count}\n'
    )
    
    if registered_at:
        text += f'<b>Регистрация:</b> {registered_at}\n'
    
    await callback.message.edit_text(text, reply_markup=admin_user_detail_keyboard(user_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'admin_broadcast')
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка сообщений</b>\n\n'
        '<blockquote><i>Выберите готовый шаблон или напишите свое сообщение</i></blockquote>',
        reply_markup=broadcast_quick_templates(),
        parse_mode="HTML"
    )
    await state.set_state(Broadcast.message)
    await callback.answer()

@router.callback_query(Broadcast.message, F.data.startswith('broadcast_template_'))
async def process_broadcast_template(callback: CallbackQuery, state: FSMContext):
    template_type = callback.data.split('_')[-1]
    
    templates = {
        'free': (
            '🎱 <b>Освободилось место на занятие!</b>\n\n'
            '<blockquote><i>Появилось свободное время для записи. '
            'Успейте забронировать удобное время!</i></blockquote>\n\n'
            '📅 Записаться: /start'
        ),
        'new': (
            '🎱 <b>Новые занятия доступны для записи!</b>\n\n'
            '<blockquote><i>Открыта запись на новые даты. '
            'Выбирайте удобное время и записывайтесь прямо сейчас!</i></blockquote>\n\n'
            '📅 Записаться: /start'
        ),
        'promo': (
            '🎱 <b>Специальное предложение!</b>\n\n'
            '<blockquote><i>Скидка 20% на первое занятие для новых учеников! '
            'Акция действует ограниченное время.</i></blockquote>\n\n'
            '📅 Записаться: /start'
        ),
        'reminder': (
            '🎱 <b>Напоминание о занятии</b>\n\n'
            '<blockquote><i>Не забудьте про ваше занятие! '
            'Ждем вас в бильярдной DoubleKiss.</i></blockquote>\n\n'
            '📋 Мои записи: /start'
        ),
        'info': (
            '🎱 <b>Уважаемые клиенты!</b>\n\n'
            '<blockquote><i>Напоминаем о режиме работы бильярдной DoubleKiss: '
            'ежедневно с 10:00 до 02:00</i></blockquote>\n\n'
            '📞 Контакты: /start'
        )
    }
    
    message_text = templates.get(template_type, "")
    
    users = await get_all_users()
    success = 0
    failed = 0
    
    status_msg = await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка</b>\n\n'
        '<blockquote><i>Отправка сообщений...</i></blockquote>',
        parse_mode="HTML"
    )
    
    for user in users:
        try:
            await callback.bot.send_message(user[0], message_text, parse_mode="HTML")
            success += 1
        except:
            failed += 1
    
    await status_msg.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка завершена!</b>\n\n'
        f'✅ <b>Успешно:</b> {success}\n'
        f'❌ <b>Ошибок:</b> {failed}',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
    await state.clear()
    await callback.answer("✅ Рассылка завершена!")

@router.callback_query(Broadcast.message, F.data == 'broadcast_custom')
async def broadcast_custom_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка сообщений</b>\n\n'
        '<blockquote><i>Введите текст сообщения для всех пользователей</i></blockquote>',
        reply_markup=cancel_button(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(Broadcast.message)
async def process_broadcast(message: Message, state: FSMContext):
    users = await get_all_users()
    success = 0
    failed = 0
    
    status_msg = await message.answer(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка</b>\n\n'
        '<blockquote><i>Отправка сообщений...</i></blockquote>',
        parse_mode="HTML"
    )
    
    for user in users:
        try:
            await message.bot.send_message(user[0], message.text)
            success += 1
        except:
            failed += 1
    
    await status_msg.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Рассылка завершена!</b>\n\n'
        f'✅ <b>Успешно:</b> {success}\n'
        f'❌ <b>Ошибок:</b> {failed}',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
    await state.clear()

# Обработка ручного ввода для даты
@router.message(AddLesson.date)
async def process_date_manual(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(date=message.text)
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    date_esc = message.text.replace('.', '\\.')
    text = f"✅ Дата: `{date_esc}`\n\n🕐 Выберите время занятия:"
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=time_quick_select(), parse_mode="MarkdownV2")
        except:
            pass
    
    await state.set_state(AddLesson.time)

# Обработка ручного ввода для времени
@router.message(AddLesson.time)
async def process_time_manual(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(time=message.text)
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    date_esc = data['date'].replace('.', '\\.')
    time_esc = message.text.replace(':', '\\:')
    
    text = (
        f"✅ Дата: `{date_esc}`\n"
        f"✅ Время: `{time_esc}`\n\n"
        "⏱ Выберите длительность:"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=duration_quick_select(), parse_mode="MarkdownV2")
        except:
            pass
    
    await state.set_state(AddLesson.duration)

# Обработка ручного ввода для длительности
@router.message(AddLesson.duration)
async def process_duration_manual(message: Message, state: FSMContext):
    await message.delete()
    
    if not message.text.isdigit():
        return
    
    await state.update_data(duration=int(message.text))
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    date_esc = data['date'].replace('.', '\\.')
    time_esc = data['time'].replace(':', '\\:')
    
    text = (
        f"✅ Дата: `{date_esc}`\n"
        f"✅ Время: `{time_esc}`\n"
        f"✅ Длительность: _{message.text} мин_\n\n"
        "💰 Выберите стоимость:"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=price_quick_select(), parse_mode="MarkdownV2")
        except:
            pass
    
    await state.set_state(AddLesson.price)

# Обработка ручного ввода для цены
@router.message(AddLesson.price)
async def process_price_manual(message: Message, state: FSMContext):
    await message.delete()
    
    if not message.text.isdigit():
        return
    
    await state.update_data(price=int(message.text))
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    date_esc = data['date'].replace('.', '\\.')
    time_esc = data['time'].replace(':', '\\:')
    
    text = (
        f"✅ Дата: `{date_esc}`\n"
        f"✅ Время: `{time_esc}`\n"
        f"✅ Длительность: _{data['duration']} мин_\n"
        f"✅ Стоимость: *{message.text}₽*\n\n"
        "📝 Выберите описание:"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=description_quick_select(), parse_mode="MarkdownV2")
        except:
            pass
    
    await state.set_state(AddLesson.description)

# Обработка ручного ввода для описания
@router.message(AddLesson.description)
async def process_description_manual(message: Message, state: FSMContext):
    await message.delete()
    
    description = message.text
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    lesson_id = await add_lesson(
        data['date'],
        data['time'],
        data['duration'],
        data['price'],
        description
    )
    
    date_esc = data['date'].replace('.', '\\.')
    time_esc = data['time'].replace(':', '\\:')
    desc_esc = description.replace('.', '\\.').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)')
    
    text = (
        "✅ *Занятие успешно добавлено\\!*\n\n"
        f"📅 Дата: `{date_esc}`\n"
        f"🕐 Время: `{time_esc}`\n"
        f"⏱ Длительность: _{data['duration']} мин_\n"
        f"💰 Стоимость: *{data['price']}₽*\n"
        f"📝 Описание: _{desc_esc}_\n"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=admin_menu(), parse_mode="MarkdownV2")
        except:
            await message.answer(text, reply_markup=admin_menu(), parse_mode="MarkdownV2")
    
    await state.clear()

    await state.clear()

@router.callback_query(F.data.startswith('admin_delete_'))
async def confirm_delete_lesson(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    lesson_id = int(callback.data.split('_')[2])
    
    # Создаем клавиатуру подтверждения
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}")
    kb.button(text="❌ Отмена", callback_data=f"admin_lesson_{lesson_id}")
    kb.adjust(2)
    
    markup = kb.as_markup()
    markup.inline_keyboard[0][0].style = "danger"
    
    await callback.message.edit_text(
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Удаление занятия</b>\n\n'
        f'<blockquote><i>Вы уверены, что хотите удалить занятие #{lesson_id}?</i></blockquote>',
        reply_markup=markup,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith('confirm_delete_'))
async def delete_lesson_confirmed(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    lesson_id = int(callback.data.split('_')[2])
    
    try:
        await delete_lesson(lesson_id)
        await callback.answer("✅ Занятие удалено!", show_alert=True)
        
        # Возвращаемся к списку занятий
        lessons = await get_available_lessons()
        
        if not lessons:
            await callback.message.edit_text(
                '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все занятия</b>\n\n'
                '<blockquote><i>Нет доступных занятий</i></blockquote>',
                reply_markup=admin_menu(),
                parse_mode="HTML"
            )
        else:
            text = (
                '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Все занятия</b>\n\n'
                '<blockquote><i>Выберите занятие для управления</i></blockquote>'
            )
            await callback.message.edit_text(text, reply_markup=admin_lessons_keyboard(lessons, 0), parse_mode="HTML")
    except Exception as e:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)

@router.callback_query(F.data == 'back_to_admin')
async def back_to_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Админ-панель DoubleKiss</b>\n\n'
        '<blockquote><i>Управление занятиями, записями и рассылками</i></blockquote>',
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


# Состояние для поиска пользователей
class UserSearch(StatesGroup):
    query = State()

@router.callback_query(F.data == 'admin_user_search')
async def start_user_search(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.button(text="◀️ Назад", callback_data="admin_users")
    markup = kb.as_markup()
    
    await callback.message.edit_text(
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Поиск пользователя</b>\n\n'
        '<blockquote><i>Введите имя, фамилию или номер телефона для поиска</i></blockquote>',
        reply_markup=markup,
        parse_mode="HTML"
    )
    await state.set_state(UserSearch.query)
    await callback.answer()

@router.message(UserSearch.query)
async def process_user_search(message: Message, state: FSMContext):
    query = message.text.lower().strip()
    users = await get_all_users()
    
    # Поиск по имени, фамилии или телефону
    found_users = []
    for user in users:
        user_id, first_name, last_name, phone, gender, age, _ = user
        if (query in first_name.lower() or 
            query in last_name.lower() or 
            query in phone):
            found_users.append(user)
    
    if not found_users:
        await message.answer(
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Результаты поиска</b>\n\n'
            '<blockquote><i>Пользователи не найдены</i></blockquote>',
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
    else:
        text = (
            f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Результаты поиска</b>\n\n'
            f'<b>Найдено пользователей:</b> {len(found_users)}\n\n'
            f'<blockquote><i>Выберите пользователя для просмотра профиля</i></blockquote>'
        )
        await message.answer(text, reply_markup=admin_users_keyboard(found_users, 0), parse_mode="HTML")
    
    await state.clear()
