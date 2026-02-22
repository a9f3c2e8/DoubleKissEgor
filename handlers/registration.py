from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database import register_user, get_user
from keyboards import gender_keyboard, main_menu, cancel_button

router = Router()

class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    gender = State()
    age = State()

def escape_md(text: str) -> str:
    """Экранирование спецсимволов для MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    
    if user:
        name = user[1]
        text = (
            f'<tg-emoji emoji-id="5418138833457793454">🎱</tg-emoji> <b>С возвращением, {name}!\nДобро пожаловать в бот бильярдной DoubleKiss!</b>\n\n'
            f'<blockquote><i>Здесь вы можете записаться на занятия к профессиональному тренеру Егору</i></blockquote>'
        )
        await message.answer(text, reply_markup=main_menu(), parse_mode="HTML")
    else:
        text = (
            "🎱 *Добро пожаловать в бот бильярдной DoubleKiss\\!*\n\n"
            "Для начала работы необходимо пройти *быструю регистрацию*\\.\n\n"
            "📝 Введите ваше *имя*:"
        )
        bot_msg = await message.answer(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
        await state.update_data(bot_message=bot_msg)
        await state.set_state(Registration.first_name)

@router.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(first_name=message.text)
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    text = "✅ *Отлично\\!*\n\nТеперь введите вашу *фамилию*:"
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
        except:
            new_msg = await message.answer(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
            await state.update_data(bot_message=new_msg)
    else:
        new_msg = await message.answer(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
        await state.update_data(bot_message=new_msg)
    
    await state.set_state(Registration.last_name)

@router.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(last_name=message.text)
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    text = (
        "📱 Введите ваш *номер телефона*:\n\n"
        "_Например:_ `\\+79991234567`"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
        except:
            new_msg = await message.answer(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
            await state.update_data(bot_message=new_msg)
    
    await state.set_state(Registration.phone)

@router.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    text = "👥 Укажите ваш *пол*:"
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=gender_keyboard(), parse_mode="MarkdownV2")
        except:
            new_msg = await message.answer(text, reply_markup=gender_keyboard(), parse_mode="MarkdownV2")
            await state.update_data(bot_message=new_msg)
    
    await state.set_state(Registration.gender)

@router.callback_query(Registration.gender, F.data.startswith('gender_'))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = 'М' if callback.data == 'gender_m' else 'Ж'
    await state.update_data(gender=gender)
    text = "🎂 Укажите ваш *возраст* \\(_полных лет_\\):"
    await callback.message.edit_text(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
    await state.set_state(Registration.age)
    await callback.answer()

@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    await message.delete()
    
    data = await state.get_data()
    bot_msg = data.get('bot_message')
    
    if not message.text.isdigit():
        text = "❌ *Ошибка\\!* Пожалуйста, введите число"
        if bot_msg:
            try:
                await bot_msg.edit_text(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
            except:
                pass
        return
    
    age = int(message.text)
    if age < 5 or age > 100:
        text = "❌ *Ошибка\\!* Пожалуйста, введите корректный возраст"
        if bot_msg:
            try:
                await bot_msg.edit_text(text, reply_markup=cancel_button(), parse_mode="MarkdownV2")
            except:
                pass
        return
    
    await register_user(
        message.from_user.id,
        data['first_name'],
        data['last_name'],
        data['phone'],
        data['gender'],
        age
    )
    
    first_name = escape_md(data['first_name'])
    last_name = escape_md(data['last_name'])
    phone = escape_md(data['phone'])
    gender = escape_md(data['gender'])
    
    text = (
        "✅ *Регистрация завершена\\!*\n\n"
        f"👤 *{first_name} {last_name}*\n"
        f"📞 `{phone}`\n"
        f"👥 Пол: _{gender}_\n"
        f"🎂 Возраст: *{age}* лет\n\n"
        "🎱 _Теперь вы можете записаться на занятия\\!_"
    )
    
    if bot_msg:
        try:
            await bot_msg.edit_text(text, reply_markup=main_menu(), parse_mode="MarkdownV2")
        except:
            await message.answer(text, reply_markup=main_menu(), parse_mode="MarkdownV2")
    else:
        await message.answer(text, reply_markup=main_menu(), parse_mode="MarkdownV2")
    
    await state.clear()

@router.callback_query(F.data == 'cancel')
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = (
        "❌ *Регистрация отменена*\n\n"
        "Для начала работы используйте /start"
    )
    await callback.message.edit_text(text, parse_mode="MarkdownV2")
    await callback.answer()
