from aiogram import Router, F
from aiogram.types import CallbackQuery

from database import get_available_lessons, get_lesson, book_lesson, get_user_bookings, get_user
from keyboards import main_menu, lessons_keyboard, confirm_booking, back_button

router = Router()

def escape_md(text: str) -> str:
    """Экранирование спецсимволов для MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

@router.callback_query(F.data == 'back_to_main')
async def back_to_main(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    name = user[1]
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>С возвращением, {name}!\nДобро пожаловать в бот бильярдной DoubleKiss!</b>\n\n'
        f'<blockquote><i>Здесь вы можете записаться на занятия к профессиональному тренеру Егору</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'book_lesson')
async def show_lessons(callback: CallbackQuery):
    lessons = await get_available_lessons()
    
    if not lessons:
        text = (
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Доступные занятия</b>\n\n'
            '<blockquote><i>К сожалению, сейчас нет доступных занятий. Попробуйте позже!</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")
    else:
        text = (
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Доступные занятия</b>\n\n'
            '<blockquote><i>Выберите удобное время для записи</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=lessons_keyboard(lessons, 0), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('lessons_page_'))
async def show_lessons_page(callback: CallbackQuery):
    page = int(callback.data.split('_')[2])
    lessons = await get_available_lessons()
    
    text = (
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Доступные занятия</b>\n\n'
        '<blockquote><i>Выберите удобное время для записи</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=lessons_keyboard(lessons, page), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('lesson_'))
async def show_lesson_details(callback: CallbackQuery):
    lesson_id = int(callback.data.split('_')[1])
    lesson = await get_lesson(lesson_id)
    
    if not lesson:
        await callback.answer("❌ Занятие не найдено", show_alert=True)
        return
    
    _, date, time, duration, price, description, is_available, _ = lesson
    
    if not is_available:
        await callback.answer("❌ Это занятие уже забронировано", show_alert=True)
        return
    
    text = (
        f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Детали занятия</b>\n\n'
        f'<b>Дата:</b> <code>{date}</code>\n'
        f'<b>Время:</b> <code>{time}</code>\n'
        f'<b>Длительность:</b> {duration} минут\n'
        f'<b>Стоимость:</b> {price}₽\n'
    )
    
    if description:
        text += f'\n<blockquote><i>{description}</i></blockquote>\n'
    
    text += '\n<b>Подтвердите запись:</b>'
    
    await callback.message.edit_text(text, reply_markup=confirm_booking(lesson_id), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith('confirm_book_'))
async def confirm_booking_handler(callback: CallbackQuery):
    lesson_id = int(callback.data.split('_')[2])
    user = await get_user(callback.from_user.id)
    
    try:
        await book_lesson(callback.from_user.id, lesson_id)
        lesson = await get_lesson(lesson_id)
        
        name = user[1]
        
        text = (
            f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Отлично, {name}!</b>\n\n'
            f'<b>Вы успешно записаны на занятие</b>\n\n'
            f'<b>Дата:</b> <code>{lesson[1]}</code>\n'
            f'<b>Время:</b> <code>{lesson[2]}</code>\n'
            f'<b>Стоимость:</b> {lesson[4]}₽\n\n'
            f'<blockquote><i>Ждем вас в бильярдной DoubleKiss!</i></blockquote>'
        )
        
        await callback.message.edit_text(text, reply_markup=main_menu(), parse_mode="HTML")
    except Exception as e:
        await callback.answer("❌ Ошибка при записи. Попробуйте позже.", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == 'my_bookings')
async def show_my_bookings(callback: CallbackQuery):
    bookings = await get_user_bookings(callback.from_user.id)
    
    if not bookings:
        text = (
            '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Ваши записи</b>\n\n'
            '<blockquote><i>У вас пока нет записей на занятия</i></blockquote>'
        )
        await callback.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")
    else:
        text = '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Ваши записи</b>\n\n'
        for booking in bookings:
            _, date, time, duration, price, description, status = booking
            status_text = "Подтверждено" if status == "confirmed" else "Ожидание"
            text += (
                f'<b>{date}</b> в <code>{time}</code>\n'
                f'· Длительность: {duration} мин\n'
                f'· Стоимость: {price}₽\n'
                f'· Статус: {status_text}\n\n'
            )
        
        await callback.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")
    
    await callback.answer()

@router.callback_query(F.data == 'about_trainer')
async def about_trainer(callback: CallbackQuery):
    text = (
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Тренер Егор</b>\n\n'
        '<b>Профессиональный игрок в бильярд</b>\n\n'
        '<blockquote><i>· Опыт преподавания: более 10 лет\n'
        '· Специализация: русский бильярд, пул\n'
        '· Индивидуальный подход к каждому ученику\n\n'
        'Егор поможет вам освоить правильную технику удара, развить тактическое мышление, '
        'улучшить точность и контроль, подготовиться к турнирам</i></blockquote>\n\n'
        '<b>Контакт:</b> @egorchuchkalov'
    )
    await callback.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'contacts')
async def contacts(callback: CallbackQuery):
    text = (
        '<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>Контакты бильярдной DoubleKiss</b>\n\n'
        '<b>Клуб на Лесной</b>\n'
        '· Адрес: Москва, ул. Лесная 20с3\n'
        '· Телефон: <code>+7 903 230 22 20</code>\n\n'
        '<b>Клуб на Трех вокзалах</b>\n'
        '· Адрес: Москва, Новорязанская улица, 23с1\n'
        '· Телефон: <code>+7 903 260 22 20</code>\n\n'
        '<blockquote><i>Режим работы: Ежедневно 10:00 - 02:00\n\n'
        'Тренер: @egorchuchkalov\n'
        'По всем вопросам обращайтесь к администратору</i></blockquote>'
    )
    await callback.message.edit_text(text, reply_markup=back_button(), parse_mode="HTML")
    await callback.answer()
