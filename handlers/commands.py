from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.keyboards import (
    get_main_keyboard,
    get_goals_keyboard,
    get_progress_keyboard,
    get_materials_keyboard
)
from utils.messages import get_message, get_user_lang, format_test_stats
from utils.states import GoalStates, MaterialStates, NoteStates, ProfileStates, SettingsStates
from utils.error_handler import handle_errors
<<<<<<< HEAD
from database import UserManager, TestResultsManager
from utils.artifacts import ARTIFACTS_BY_PROFESSION
=======
import aiohttp
from config import settings
>>>>>>> 84bfe15ac6710e0105e1b6ec45e2f0881e027c07

router = Router()

@router.message(Command("start"))
@handle_errors
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    lang = await get_user_lang(message.from_user.id)
    welcome_texts = {
        'ru': (
            "<b>Добро пожаловать в SkillPath!</b>\n\n"
            "🧩 <b>SkillPath</b> — это профориентационный квест-бот, который поможет тебе открыть свои сильные стороны, узнать о профессиях будущего и собрать уникальную коллекцию артефактов!\n\n"
            "🔍 Пройди интерактивный тест, чтобы узнать, какой путь тебе ближе всего.\n"
            "🗝️ Открывай порталы, собирай артефакты и персональные советы по профессиям.\n"
            "📊 Следи за своим прогрессом, возвращайся к тесту и открывай новые возможности!\n\n"
            "<i>Каждый твой выбор — шаг к мечте. Готов начать путешествие?</i>"
        ),
        'ky': (
            "<b>SkillPath'ка кош келиңиз!</b>\n\n"
            "🧩 <b>SkillPath</b> — бул кесиптик багыт берүүчү квест-бот. Ал сага күчтүү жактарыңды ачууга, келечектеги кесиптер менен таанышууга жана уникалдуу артефакттарды чогултууга жардам берет!\n\n"
            "🔍 Интерактивдүү тесттен өтүп, сага ылайыктуу жолду бил.\n"
            "🗝️ Порталдарды ач, артефакттарды топто жана кесиптер боюнча жеке кеңештерди ал.\n"
            "📊 Прогрессти көзөмөлдө, тестке кайтып, жаңы мүмкүнчүлүктөрдү ач!\n\n"
            "<i>Ар бир тандооң — кыялга карай кадам. Саякатыңды баштоого даярсыңбы?</i>"
        )
    }
    await message.answer(
        welcome_texts[lang],
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["🎯 Мои цели", "🎯 Максаттарым"]))
@handle_errors
async def show_goals_menu(message: Message):
    """Показать меню целей."""
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_message("goals_menu", lang),
        reply_markup=get_goals_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["📊 Прогресс", "📊 Прогресс"]))
@handle_errors
async def show_progress_menu(message: Message):
    """Показать меню прогресса."""
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_message("progress_menu", lang),
        reply_markup=get_progress_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["📚 Материалы", "📚 Материалдар"]))
@handle_errors
async def show_materials_menu(message: Message):
    """Показать меню материалов."""
    lang = await get_user_lang(message.from_user.id)
    await message.answer(
        get_message("materials_menu", lang),
        reply_markup=get_materials_keyboard(lang),
        parse_mode="HTML"
    )

@router.message(F.text.in_(["❓ Помощь", "❓ Жардам"]))
@handle_errors
async def show_help(message: Message):
    lang = await get_user_lang(message.from_user.id)
    # Новое атмосферное сообщение помощи
    help_texts = {
        'ru': (
            "<b>❓ Помощь</b>\n\n"
            "<i>SkillPath — твой проводник в мире профессий и открытий!</i>\n\n"
            "<b>🧭 Что ты можешь здесь?</b>\n"
            "• 🧩 <b>Тест</b> — пройти профориентационный квест и узнать свои сильные стороны.\n"
            "• 🗝️ <b>Коллекция</b> — собирать уникальные артефакты и открывать порталы.\n"
            "• 📊 <b>Статистика</b> — отслеживать свой путь и достижения.\n"
            "• 👤 <b>Профиль</b> — видеть свой прогресс и ачивки.\n"
            "• 🌍 <b>Сменить язык</b> — выбрать язык общения.\n\n"
            "<b>✨ Не бойся пробовать новое — каждый шаг открывает новые горизонты!</b>\n\n"
            "Если возникли вопросы — напиши /start или воспользуйся кнопками ниже!"
        ),
        'ky': (
            "<b>❓ Жардам</b>\n\n"
            "<i>SkillPath — кесиптер жана ачылыштар дүйнөсүндөгү сенин жол көрсөтүүчүң!</i>\n\n"
            "<b>🧭 Бул жерде эмне кыла аласың?</b>\n"
            "• 🧩 <b>Тест</b> — профориентациялык квесттен өтүп, күчтүү жактарыңды бил.\n"
            "• 🗝️ <b>Коллекция</b> — уникалдуу артефакттарды чогулт жана порталдарды ач.\n"
            "• 📊 <b>Статистика</b> — жетишкендиктериңди көзөмөлдө.\n"
            "• 👤 <b>Профиль</b> — прогресс жана ачивкаларды көр.\n"
            "• 🌍 <b>Тилди өзгөртүү</b> — тилди танда.\n\n"
            "<b>✨ Жаңы нерселерден коркпо — ар бир кадам жаңы горизонтторду ачат!</b>\n\n"
            "Суроолор болсо — /start деп жаз же төмөнкү баскычтарды колдон!"
        )
    }
    await message.answer(help_texts[lang], parse_mode="HTML")

@router.message(Command("profile"))
@handle_errors
async def cmd_profile(message: Message, state: FSMContext):
    """Начать настройку профиля."""
    await state.set_state(ProfileStates.waiting_for_name)
    await message.answer("👤 Как вас зовут?")

@router.message(Command("cancel"))
@handle_errors
async def cmd_cancel(message: Message, state: FSMContext):
    """Отменить текущее действие."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нечего отменять.")
        return

    await state.clear()
    await message.answer(
        "✅ Действие отменено.",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text.in_(["📊 Статистика", "📊 Статистика"]))
@handle_errors
async def show_stats(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
<<<<<<< HEAD
    results = await TestResultsManager.get_user_results(user_id)
=======
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{settings.API_URL}/test_results/?telegram_id={user_id}") as resp:
            results = await resp.json()
>>>>>>> 84bfe15ac6710e0105e1b6ec45e2f0881e027c07
    if not results:
        await message.answer(get_message("stats_none", lang))
        return
    text = format_test_stats(results, lang)
    await message.answer(text, parse_mode="HTML")

@router.message(F.text.in_(["🌍 Сменить язык", "🌍 Тилди өзгөртүү"]))
@handle_errors
async def change_language_menu(message: Message, state: FSMContext):
    LANG_INLINE_KB = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
             InlineKeyboardButton(text="Кыргызский", callback_data="lang_ky")]
        ]
    )
    await message.answer("Выберите язык для использования в боте:", reply_markup=LANG_INLINE_KB)
    await state.set_state(SettingsStates.waiting_for_language)

@router.message(F.text.in_(["👤 Профиль", "/profile"]))
@handle_errors
async def show_profile(message: Message):
    user_id = message.from_user.id
    lang = await get_user_lang(user_id)
<<<<<<< HEAD
    user = await UserManager.get_user(user_id)
    if not user:
        await message.answer("Профиль не найден. Пожалуйста, пройдите регистрацию.")
        return
=======
    # --- Получаем данные из API ---
    user_api = {}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.API_URL}/users/?telegram_id={user_id}") as resp:
                if resp.status == 200:
                    user_api = await resp.json()
    except Exception as e:
        print(f"[DEBUG] Ошибка получения профиля из API: {e}")
>>>>>>> 84bfe15ac6710e0105e1b6ec45e2f0881e027c07
    # --- Получаем данные из локальной базы ---
    # db_data = db._read_db()
    # user_local = db_data.get('users', {}).get(str(user_id), {})
    # --- Объединяем данные: приоритет — API ---
    def get_field(field, default="-"):
        return user.get(field) or default
    fio = get_field('fio')
    school = get_field('school')
    class_number = get_field('class_number')
    class_letter = get_field('class_letter')
    city = get_field('city')
    language = get_field('language', lang)
    gender = get_field('gender')
    birth_year = get_field('birth_year')
    # --- Прогресс по артефактам ---
    portals_local = set(user.get('portals', []) or [])
    artifacts_api = set(user.get('artifacts', []) or [])
    portals = portals_local.union(artifacts_api)
    total_artifacts = 60 if len(ARTIFACTS_BY_PROFESSION) < 60 else len(ARTIFACTS_BY_PROFESSION)
    collected = len(portals)
    # Красивый прогресс-бар
    bar_len = 20
    filled = int(bar_len * collected / total_artifacts)
    progress_bar = f"{'🟩'*filled}{'⬜️'*(bar_len-filled)} {collected}/{total_artifacts}"
    # --- Уникальные профессии и тесты ---
    unique_professions = set()
    results = []
    try:
<<<<<<< HEAD
        results = await TestResultsManager.get_user_results(user_id)
=======
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.API_URL}/test_results/?telegram_id={user_id}") as resp:
                if resp.status == 200:
                    results = await resp.json()
>>>>>>> 84bfe15ac6710e0105e1b6ec45e2f0881e027c07
    except Exception as e:
        print(f"[DEBUG] Ошибка получения тестов из API: {e}")
    for r in results:
        prof = r.get('profile')
        if prof:
            unique_professions.add(prof)
    # Ачивка за все артефакты
    all_collected = collected == total_artifacts
    achiev = "🏆" if all_collected else ""
    # Мультиязычные подписи и вдохновляющая шапка
    profile_headers = {
        'ru': "<b>🦊 Твой герой в SkillPath</b>\n\n<code>✨ Каждый артефакт — твоя победа! ✨</code>",
        'ky': "<b>🦊 SkillPathтагы сенин баатырыӊ</b>\n\n<code>✨ Ар бир артефакт — сенин жетишкендигиӊ! ✨</code>"
    }
    labels = {
        'ru': {
            'fio': '📜 Имя', 'school': '🏫 Школа', 'class': '🎒 Класс', 'city': '🌍 Город', 'lang': '🗣️ Язык',
            'gender': '🧑‍🤝‍🧑 Пол', 'birth_year': '📅 Год рождения',
            'artifacts': '🗝️ Артефакты', 'professions': '🌈 Уникальные профили', 'tests': '🧩 Тестов пройдено',
            'progress': '📊 Прогресс коллекции', 'achiev': '🏅 Ачивки',
        },
        'ky': {
            'fio': '📜 Аты-жөнү', 'school': '🏫 Мектеп', 'class': '🎒 Класс', 'city': '🌍 Шаар', 'lang': '🗣️ Тил',
            'gender': '🧑‍🤝‍🧑 Жынысы', 'birth_year': '📅 Туулган жылы',
            'artifacts': '🗝️ Артефакттар', 'professions': '🌈 Уникалдуу профилдер', 'tests': '🧩 Тесттер',
            'progress': '📊 Коллекциянын прогресси', 'achiev': '🏅 Ачиивкалар',
        }
    }[lang]
    # Человеко-понятный язык
    lang_map = {"ru": "Русский", "ky": "Кыргызский", None: "Не выбран", "русский": "Русский", "кыргызский": "Кыргызский"}
    language_human = lang_map.get(str(language).lower(), language or "-")
    gender_human = gender.capitalize() if gender else "-"
    # Мотивация
    motivation = {
        'ru': "<i>Продолжай собирать артефакты, открывай новые порталы и вдохновляйся своим прогрессом! Ты — герой своего пути! 🦊</i>",
        'ky': "<i>Жаңы артефакттарды чогулт, порталдарды ач жана прогрессиӊ менен сыймыктан! Сен — өз жолуӊдун баатырысыӊ! 🦊</i>"
    }[lang]
    # --- Переводим уникальные профили для вывода ---
    from handlers.test import PROFILE_TRANSLATIONS
    unique_professions_display = [PROFILE_TRANSLATIONS[lang].get(p, p) for p in unique_professions]
    # Формируем текст профиля
    text_lines = [
        profile_headers[lang],
        "",
        f"{labels['fio']}: <b>{fio}</b>",
        f"{labels['school']}: <b>{school}</b>",
        f"{labels['class']}: <b>{class_number}{class_letter}</b>",
        f"{labels['city']}: <b>{city}</b>",
        f"{labels['lang']}: <b>{language_human}</b>",
        f"{labels['gender']}: <b>{gender_human}</b>",
        f"{labels['birth_year']}: <b>{birth_year}</b>",
        "",
        f"{labels['artifacts']}: <b>{collected}/{total_artifacts}</b>  {achiev}",
        f"{labels['progress']}: {progress_bar}",
        f"{labels['professions']}: <b>{len(unique_professions_display)}</b>"
    ]
    if lang == 'ky' and unique_professions_display:
        text_lines.append(f"<b>{', '.join(unique_professions_display)}</b>")
    text_lines.append(f"{labels['tests']}: <b>{len(results)}</b>")
    text_lines.append("")
    text_lines.append(motivation)
    text = "\n".join(text_lines)
    await message.answer(text, parse_mode="HTML")

def register_handlers(dispatcher):
    dispatcher.include_router(router)