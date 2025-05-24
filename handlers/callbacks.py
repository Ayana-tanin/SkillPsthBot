from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import json

from utils.error_handler import handle_errors
from utils.messages import get_message, normalize_lang, get_user_lang
from utils.keyboards import (
    get_main_keyboard,
    get_goals_keyboard,
    get_progress_keyboard,
    get_materials_keyboard,
    get_settings_keyboard
)
from utils.states import RegistrationStates
from utils.states import SettingsStates
from database import UserManager

router = Router()

LANG_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="Кыргызский", callback_data="lang_ky")]
    ]
)

@router.callback_query(F.data == "back_to_main")
@handle_errors
async def back_to_main(callback: CallbackQuery):
    """Возврат в главное меню."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_message("welcome", lang)
    )
    await callback.message.answer(
        get_message("welcome", lang),
        reply_markup=get_main_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "goals_menu")
@handle_errors
async def show_goals_menu(callback: CallbackQuery):
    """Показать меню целей."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_message("goals_menu", lang),
        reply_markup=get_goals_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "progress_menu")
@handle_errors
async def show_progress_menu(callback: CallbackQuery):
    """Показать меню прогресса."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_message("progress_menu", lang),
        reply_markup=get_progress_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "materials_menu")
@handle_errors
async def show_materials_menu(callback: CallbackQuery):
    """Показать меню материалов."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_message("materials_menu", lang),
        reply_markup=get_materials_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "settings_menu")
@handle_errors
async def show_settings_menu(callback: CallbackQuery):
    """Показать меню настроек."""
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.edit_text(
        get_message("settings", lang),
        reply_markup=get_settings_keyboard(lang)
    )
    await callback.answer()

@router.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выберите язык для использования в боте:",
        reply_markup=LANG_INLINE_KB
    )
    await state.set_state(SettingsStates.waiting_for_language)
    await callback.answer()

@router.callback_query(F.data.in_(["lang_ru", "lang_ky"]))
async def set_language_callback(callback: CallbackQuery, state: FSMContext):
    lang = "ru" if callback.data == "lang_ru" else "ky"
    user_id = callback.from_user.id
    # Обновляем язык пользователя в базе
    await UserManager.update_user(user_id, language=lang)
    await callback.message.edit_text(get_message("language_changed", lang, lang_name="Кыргызский" if lang == "ky" else "Русский"))
    await state.clear()
    await callback.message.answer(get_message("welcome", lang), reply_markup=get_main_keyboard(lang))
    await callback.answer()

@router.callback_query(F.data == "update_main_menu")
async def update_main_menu(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    await callback.message.answer(get_message("welcome", lang), reply_markup=get_main_keyboard(lang))
    await callback.answer()

@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_lang(user_id)
    user = await UserManager.get_user(user_id)
    if not user or not user.get("telegram_id"):
        await callback.message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию.")
        await callback.answer()
        return
    # Человеко-понятный язык
    lang_map = {"ru": "Русский", "ky": "Кыргызский", None: "Не выбран", "русский": "Русский", "кыргызский": "Кыргызский"}
    user_lang = user.get('language')
    user_lang = lang_map.get(str(user_lang).lower(), user_lang or "-")
    # Креативный шаблон
    if lang == "ky":
        text = (
            "🧙‍♂️ <b>Сенин SkillPath баатырың</b>\n\n"
            f"📜 <b>Аты-жөнү:</b> {user.get('fio', '-') }\n"
            f"🏫 <b>Мектеп:</b> {user.get('school', '-') }\n"
            f"🎒 <b>Класс:</b> {user.get('class_number', '-') }{user.get('class_letter', '')}\n"
            f"🧑‍🤝‍🧑 <b>Жынысы:</b> {user.get('gender', '-') }\n"
            f"📅 <b>Туулган жылы:</b> {user.get('birth_year', '-') }\n"
            f"🌍 <b>Шаар/айыл:</b> {user.get('city', '-') }\n"
            f"🗣️ <b>Тил:</b> {user_lang}\n\n"
            "✨ <i>Бул профиль — сенин билим жана ачылыштар дүйнөсүнө жолдомоң. Ар бир кадамың ийгиликтүү болсун!</i>"
        )
    else:
        text = (
            "🧙‍♂️ <b>Твой герой в SkillPath</b>\n\n"
            f"📜 <b>Имя:</b> {user.get('fio', '-') }\n"
            f"🏫 <b>Школа:</b> {user.get('school', '-') }\n"
            f"🎒 <b>Класс:</b> {user.get('class_number', '-') }{user.get('class_letter', '')}\n"
            f"🧑‍🤝‍🧑 <b>Пол:</b> {user.get('gender', '-') }\n"
            f"📅 <b>Год рождения:</b> {user.get('birth_year', '-') }\n"
            f"🌍 <b>Город:</b> {user.get('city', '-') }\n"
            f"🗣️ <b>Язык:</b> {user_lang}\n\n"
            "✨ <i>Этот профиль — твой пропуск в мир приключений, знаний и новых открытий. Пусть каждый шаг будет ярким!</i>"
        )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

def register_handlers(dispatcher):
    """Регистрация обработчиков."""
    dispatcher.include_router(router)