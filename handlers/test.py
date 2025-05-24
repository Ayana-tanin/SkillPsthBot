from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from utils.states import TestStates, RegistrationStates
from utils.scene_manager import scene_manager, SceneManager
from aiogram.filters import Command
from utils.messages import get_message, normalize_lang, get_user_lang, ARTIFACTS_BY_PROFESSION
from handlers.test_utils import start_test_flow, send_scene
import json
from datetime import datetime
import random
from collections import defaultdict
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import re
from database import UserManager, TestProgressManager, TestResultsManager
from utils.artifacts import ARTIFACTS_BY_PROFESSION
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

PROFILE_DESCRIPTIONS = {
    'Исследователь': {
        'ru': 'Тебя привлекает всё неизведанное, ты любишь искать новые подходы и открывать новые знания. Ты не боишься экспериментировать.',
        'ky': 'Сени белгисиз нерселер кызыктырат, сен жаңы ыкмаларды издеп, жаңы билимдерди ачканды жактырасың. Эксперименттен коркпойсуң.'
    },
    'Аналитик': {
        'ru': 'Ты любишь анализировать информацию, находить закономерности и решать сложные задачи. Тебе нравится работать с данными и делать логические выводы.',
        'ky': 'Маалыматтарды талдоону, мыйзам ченемдүүлүктөрдү табууну жана татаал маселелерди чечүүнү жактырасың. Маалымат менен иштеп, логикалык тыянактарды чыгаруу сага жагат.'
    },
    'Творец': {
        'ru': 'У тебя богатое воображение и нестандартное мышление. Ты умеешь видеть красоту и создавать что-то новое.',
        'ky': 'Сенин бай кыялың жана өзгөчө ой жүгүртүүң бар. Сен сулуулукту көрө билесиң жана жаңы нерселерди жарата аласың.'
    },
    'Технарь': {
        'ru': 'Ты увлекаешься технологиями, любишь разбираться в устройствах и создавать что-то своими руками.',
        'ky': 'Сен технологияларга кызыгасың, түзүлүштөрдүн ичин түшүнгөндү жана өз колуң менен бир нерсе жасаганды жактырасың.'
    },
    'Коммуникатор': {
        'ru': 'Ты легко находишь общий язык с людьми, умеешь слушать и доносить свои мысли.',
        'ky': 'Сен адамдар менен тил табышууда жеңил, угуп жана ойлоруңду жеткире билесиң.'
    },
    'Организатор': {
        'ru': 'Ты умеешь планировать, распределять задачи и вести команду к цели.',
        'ky': 'Сен пландаштырып, тапшырмаларды бөлүштүрүп, команданы максатка жеткире аласың.'
    },
    'Визуальный художник': {
        'ru': 'Ты видишь мир через призму цвета и формы, умеешь создавать визуальные образы.',
        'ky': 'Сен дүйнөнү түс жана форма аркылуу көрөсүң, визуалдык образдарды жарата аласың.'
    },
    'Цифровой художник': {
        'ru': 'Ты творишь в цифровой среде, создаёшь графику, анимацию или дизайн.',
        'ky': 'Сен санарип чөйрөдө жаратасың, графика, анимация же дизайн түзөсүң.'
    },
    'Писатель': {
        'ru': 'Ты умеешь выражать мысли через слова, создавать тексты и истории.',
        'ky': 'Сен ойлоруңду сөздөр аркылуу билдирип, тексттерди жана окуяларды жарата аласың.'
    },
    'Эколог': {
        'ru': 'Ты заботишься о природе и стремишься сделать мир чище и лучше.',
        'ky': 'Сен жаратылышты коргойсуң жана дүйнөнү тазараак жана жакшыраак кылууга умтуласың.'
    },
    'Ученый-естественник': {
        'ru': 'Ты любишь исследовать законы природы и проводить эксперименты.',
        'ky': 'Сен табият мыйзамдарын изилдеп, эксперименттерди жүргүзгөндү жактырасың.'
    },
    'Социолог': {
        'ru': 'Тебе интересно, как устроено общество и как люди взаимодействуют.',
        'ky': 'Сага коомдун түзүлүшү жана адамдардын өз ара мамилеси кызыктуу.'
    },
    'Историк': {
        'ru': 'Ты любишь изучать прошлое и находить закономерности в истории.',
        'ky': 'Сен өткөн мезгилди изилдеп, тарыхтагы мыйзам ченемдүүлүктөрдү табууну жактырасың.'
    },
    'Психолог': {
        'ru': 'Ты разбираешься в людях и их мотивах, умеешь слушать и поддерживать.',
        'ky': 'Сен адамдарды жана алардын мотивдерин түшүнөсүң, угуп жана колдой аласың.'
    },
    'Инженер-системотехник': {
        'ru': 'Ты проектируешь сложные системы и делаешь их эффективными.',
        'ky': 'Сен татаал системаларды долбоорлоп, аларды натыйжалуу кыласың.'
    },
    'Программист': {
        'ru': 'Ты создаёшь программы и цифровые решения для разных задач.',
        'ky': 'Сен ар түрдүү маселелер үчүн программаларды жана санарип чечимдерди түзөсүң.'
    },
    'Инженер данных': {
        'ru': 'Ты умеешь работать с большими объёмами информации и извлекать из них пользу.',
        'ky': 'Сен чоң көлөмдөгү маалымат менен иштеп, андан пайда чыгара аласың.'
    },
    'Робототехник': {
        'ru': 'Ты создаёшь умные машины и автоматизируешь процессы.',
        'ky': 'Сен акылдуу машиналарды түзүп, процесстерди автоматташтырасың.'
    },
    'Инженер-конструктор': {
        'ru': 'Ты придумываешь и собираешь новые устройства и механизмы.',
        'ky': 'Сен жаңы түзүлүштөрдү жана механизмдерди ойлоп табып, чогултасың.'
    },
    'Электронщик': {
        'ru': 'Ты разбираешься в электронике и любишь паять и собирать схемы.',
        'ky': 'Сен электрониканы түшүнөсүң жана схемаларды ширетип, чогултканды жактырасың.'
    },
    'Программист-интерфейсов': {
        'ru': 'Ты делаешь интерфейсы удобными и красивыми.',
        'ky': 'Сен интерфейстерди ыңгайлуу жана кооз кыласың.'
    },
    'Программист серверных систем': {
        'ru': 'Ты отвечаешь за логику и надёжность серверной части.',
        'ky': 'Сен сервер бөлүгүнүн логикасы жана ишенимдүүлүгү үчүн жооптуусуң.'
    },
    'Системный инженер': {
        'ru': 'Ты проектируешь архитектуру и инфраструктуру проектов.',
        'ky': 'Сен долбоорлордун архитектурасын жана инфраструктурасын долбоорлойсуң.'
    },
    'Организатор мероприятий': {
        'ru': 'Ты умеешь организовывать события и объединять людей.',
        'ky': 'Сен иш-чараларды уюштуруп, адамдарды бириктире аласың.'
    },
    'Фасилитатор': {
        'ru': 'Ты помогаешь команде работать эффективно и достигать целей.',
        'ky': 'Сен командага натыйжалуу иштеп, максаттарга жетүүгө жардам бересиң.'
    },
    'PR-специалист': {
        'ru': 'Ты умеешь доносить информацию до широкой аудитории.',
        'ky': 'Сен маалыматты кеңири аудиторияга жеткире аласың.'
    },
    'Маркетолог': {
        'ru': 'Ты анализируешь рынок и помогаешь продвигать продукты.',
        'ky': 'Сен базарды талдап, продуктуларды илгерилетүүгө жардам бересиң.'
    },
    'Аналитик данных': {
        'ru': 'Ты ищешь закономерности в данных и строишь прогнозы.',
        'ky': 'Сен маалыматтардагы мыйзам ченемдүүлүктөрдү таап, болжолдоолорду түзөсүң.'
    },
    'Системный аналитик': {
        'ru': 'Ты анализируешь процессы и предлагаешь оптимальные решения.',
        'ky': 'Сен процесстерди талдап, оптималдуу чечимдерди сунуштайсың.'
    },
    'Финансовый аналитик': {
        'ru': 'Ты разбираешься в финансах и умеешь считать деньги.',
        'ky': 'Сен финансыны түшүнүп, акчаны эсептей аласың.'
    },
    'Логик': {
        'ru': 'Ты любишь решать логические задачи и строить цепочки рассуждений.',
        'ky': 'Сен логикалык маселелерди чечип, ой жүгүртүү чынжырларын түзгөндү жактырасың.'
    },
    'Дизайнер пространства': {
        'ru': 'Ты создаёшь гармоничные и функциональные пространства.',
        'ky': 'Сен гармониялуу жана функционалдык мейкиндиктерди түзөсүң.'
    },
    'Исполнительский художник': {
        'ru': 'Ты выражаешь себя через музыку, театр или выступления.',
        'ky': 'Сен өзүңдү музыка, театр же чыгып сүйлөө аркылуу билдиресиң.'
    }
}

PROFILE_EMOJIS = {
    'Исследователь': '🧑‍🔬',
    'Техник': '🤖',
    'Гуманитарий': '📚',
    'Творец': '🎨',
    'Социально-экономический': '💼',
    'Прикладные технологии': '🔧',
}

PROFILE_JOBS = {
    'Исследователь': {
        'ru': ['Научный сотрудник', 'Лаборант', 'Data Scientist'],
        'ky': ['Илимий кызматкер', 'Лаборант', 'Маалымат илимпозу']
    },
    'Аналитик': {
        'ru': ['Бизнес-аналитик', 'Финансовый аналитик', 'Data Analyst'],
        'ky': ['Бизнес-аналитик', 'Финансы аналитиги', 'Маалымат аналитиги']
    },
    'Творец': {
        'ru': ['Дизайнер', 'Архитектор', 'Креативный директор'],
        'ky': ['Дизайнер', 'Архитектор', 'Чыгармачыл директор']
    },
    'Технарь': {
        'ru': ['Инженер', 'Разработчик', 'Техник'],
        'ky': ['Инженер', 'Иштеп чыгуучу', 'Техник']
    },
    'Коммуникатор': {
        'ru': ['PR-менеджер', 'Журналист', 'Учитель'],
        'ky': ['PR-менеджер', 'Журналист', 'Мугалим']
    },
    'Организатор': {
        'ru': ['Менеджер проектов', 'Администратор', 'Event-менеджер'],
        'ky': ['Долбоор менеджери', 'Администратор', 'Иш-чара уюштуруучу']
    },
    'Визуальный художник': {
        'ru': ['Художник', 'Иллюстратор', 'Декоратор'],
        'ky': ['Сүрөтчү', 'Иллюстратор', 'Декоратор']
    },
    'Цифровой художник': {
        'ru': ['Графический дизайнер', '3D-аниматор', 'UI/UX дизайнер'],
        'ky': ['Графикалык дизайнер', '3D-аниматор', 'UI/UX дизайнер']
    },
    'Писатель': {
        'ru': ['Копирайтер', 'Редактор', 'Сценарист'],
        'ky': ['Копирайтер', 'Редактор', 'Сценарист']
    },
    'Эколог': {
        'ru': ['Эколог', 'Специалист по устойчивому развитию'],
        'ky': ['Эколог', 'Туруктуу өнүгүү боюнча адис']
    },
    'Ученый-естественник': {
        'ru': ['Биолог', 'Физик', 'Химик'],
        'ky': ['Биолог', 'Физик', 'Химик']
    },
    'Социолог': {
        'ru': ['Социолог', 'Исследователь общественного мнения'],
        'ky': ['Социолог', 'Коомдук пикирди изилдөөчү']
    },
    'Историк': {
        'ru': ['Историк', 'Архивист'],
        'ky': ['Тарыхчы', 'Архивчи']
    },
    'Психолог': {
        'ru': ['Психолог', 'Консультант'],
        'ky': ['Психолог', 'Кеңешчи']
    },
    'Инженер-системотехник': {
        'ru': ['Системный инженер', 'Архитектор систем'],
        'ky': ['Система инженери', 'Системалар архитектору']
    },
    'Программист': {
        'ru': ['Разработчик ПО', 'Web-разработчик'],
        'ky': ['Программа иштеп чыгуучу', 'Веб-иштеп чыгуучу']
    },
    'Инженер данных': {
        'ru': ['Data Engineer', 'Аналитик данных'],
        'ky': ['Маалымат инженери', 'Маалымат аналитиги']
    },
    'Робототехник': {
        'ru': ['Инженер-робототехник', 'Мехатроник'],
        'ky': ['Робототехник инженер', 'Мехатроник']
    },
    'Инженер-конструктор': {
        'ru': ['Инженер-конструктор', 'Проектировщик'],
        'ky': ['Инженер-конструктор', 'Долбоорлоочу']
    },
    'Электронщик': {
        'ru': ['Инженер-электронщик', 'Схемотехник'],
        'ky': ['Электроника инженери', 'Схема техниги']
    },
    'Программист-интерфейсов': {
        'ru': ['Frontend-разработчик', 'UI-разработчик'],
        'ky': ['Frontend-иштеп чыгуучу', 'UI-иштеп чыгуучу']
    },
    'Программист серверных систем': {
        'ru': ['Backend-разработчик', 'DevOps-инженер'],
        'ky': ['Backend-иштеп чыгуучу', 'DevOps-инженер']
    },
    'Системный инженер': {
        'ru': ['Системный архитектор', 'DevOps-инженер'],
        'ky': ['Система архитектору', 'DevOps-инженер']
    },
    'Организатор мероприятий': {
        'ru': ['Event-менеджер', 'Координатор проектов'],
        'ky': ['Иш-чара уюштуруучу', 'Долбоор координатору']
    },
    'Фасилитатор': {
        'ru': ['Фасилитатор', 'Модератор'],
        'ky': ['Фасилитатор', 'Модератор']
    },
    'PR-специалист': {
        'ru': ['PR-менеджер', 'Специалист по коммуникациям'],
        'ky': ['PR-менеджер', 'Коммуникация боюнча адис']
    },
    'Маркетолог': {
        'ru': ['Маркетолог', 'Бренд-менеджер'],
        'ky': ['Маркетолог', 'Бренд-менеджер']
    },
    'Аналитик данных': {
        'ru': ['Data Analyst', 'BI-аналитик'],
        'ky': ['Маалымат аналитиги', 'BI-аналитик']
    },
    'Системный аналитик': {
        'ru': ['Системный аналитик', 'Бизнес-аналитик'],
        'ky': ['Система аналитиги', 'Бизнес-аналитик']
    },
    'Финансовый аналитик': {
        'ru': ['Финансовый аналитик', 'Экономист'],
        'ky': ['Финансы аналитиги', 'Экономист']
    },
    'Логик': {
        'ru': ['Математик', 'Разработчик алгоритмов'],
        'ky': ['Математик', 'Алгоритм иштеп чыгуучу']
    },
    'Дизайнер пространства': {
        'ru': ['Дизайнер интерьера', 'Архитектор'],
        'ky': ['Интерьер дизайнери', 'Архитектор']
    },
    'Исполнительский художник': {
        'ru': ['Актёр', 'Музыкант', 'Ведущий мероприятий'],
        'ky': ['Актёр', 'Музыкант', 'Иш-чара алып баруучу']
    }
}

RECOMMENDATION = {
    'ru': '✨ SkillPath рекомендует: Развивай свои сильные стороны и пробуй себя в разных направлениях. Мир профессий постоянно меняется, и твои уникальные качества могут быть востребованы в самых разных сферах!',
    'ky': '✨ SkillPath кеңеш берет: Күчтүү жактарыңды өнүктүр жана ар кандай багыттарда өзүңдү сына. Кесиптер дүйнөсү дайыма өзгөрөт, сенин уникалдуу сапаттарың ар түрдүү тармактарда керек болушу мүмкүн!'
}

# --- Словарь соответствия кыргызских и русских профилей ---
KY_TO_RU_PROFILE = {
    'Техническая': 'Техническая',
    'Гуманитарная': 'Гуманитарная',
    'Естественно-научная': 'Жаратылыш таануу',
    'Социально-экономическая': 'Социально-экономическая',
    'Творческо-художественная': 'Чыгармачыл-көркөм',
    'Прикладно-технологическая': 'Колдонмо-технологиялык',
}

# --- Словарь переводов профилей для локализации ---
PROFILE_TRANSLATIONS = {
    "ru": {},
    "ky": {
        "Техническая": "Техникалык",
        "Гуманитарная": "Гуманитардык",
        "Естественно-научная": "Жаратылыш таануу",
        "Социально-экономическая": "Социалдык-экономикалык",
        "Творческо-художественная": "Чыгармачыл-көркөм",
        "Прикладно-технологическая": "Колдонмо-технологиялык",
    }
}

async def get_user_data_from_db(telegram_id: int):
    """Получение данных пользователя из базы данных"""
    try:
        user = await UserManager.get_user(telegram_id)
        if not user:
            logger.warning(f"Пользователь {telegram_id} не найден в базе данных")
            return None
        return user
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя: {e}")
        return None

async def load_test_progress(telegram_id):
    """Загрузка прогресса теста из базы данных"""
    try:
        progress = await TestProgressManager.get_progress(telegram_id)
        if not progress:
            return None
        return progress
    except Exception as e:
        logger.error(f"Ошибка при загрузке прогресса теста: {e}")
        return None

async def save_test_progress(telegram_id, scene_index, all_scenes, profile_scores, profession_scores, lang):
    """Сохранение прогресса теста в базу данных"""
    try:
        await TestProgressManager.save_progress(
            telegram_id=telegram_id,
            scene_index=scene_index,
            all_scenes=all_scenes,
            profile_scores=profile_scores,
            profession_scores=profession_scores,
            lang=lang
        )
    except Exception as e:
        logger.error(f"Ошибка при сохранении прогресса теста: {e}")

async def delete_test_progress(telegram_id):
    """Удаление прогресса теста из базы данных"""
    try:
        await TestProgressManager.delete_progress(telegram_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении прогресса теста: {e}")

@router.message(Command("test"))
async def start_test(message: Message, state: FSMContext):
    user_data = await get_user_data_from_db(message.from_user.id)
    if not user_data or not user_data.get("fio"):
        lang = await get_user_lang(message.from_user.id)
        await message.answer(get_message("register", lang))
        await state.clear()
        await state.set_state(RegistrationStates.waiting_for_fio)
        await message.answer(get_message("registration_fio", lang))
        return
    # --- ПРОВЕРКА ПРОГРЕССА ---
    progress = await load_test_progress(message.from_user.id)
    # Проверяем, что прогресс валидный: не персональные сцены и не завершён
    valid_progress = False
    if progress and progress.get("all_scenes") and progress.get("scene_index", 0) < len(progress["all_scenes"]):
        all_scenes = progress["all_scenes"]
        # Проверяем, что это именно базовые сцены (например, по id первой сцены)
        if all_scenes and all_scenes[0].get("id", 0) == 1:
            valid_progress = True
    if valid_progress:
        await state.update_data(**progress)
        all_scenes = progress["all_scenes"]
        scene_index = progress["scene_index"]
        await send_scene(message, all_scenes[scene_index], state=state)
        return
    # Если прогресс невалидный или завершён — очищаем и стартуем заново
    await delete_test_progress(message.from_user.id)
    from handlers.test_utils import start_test_flow
    await start_test_flow(message, state)

@router.message(F.text.in_(["🧩 Тест", "🧩 Тест"]))
async def start_test_button(message: Message, state: FSMContext):
    await start_test(message, state)

import random

CREATIVE_TEXTS = {
    'ru': [
    "✨ Ты сделал выбор! Путь продолжается...",
    "🚀 Каждый шаг — это новое открытие!",
    "🌟 Отлично! Двигаемся дальше!",
    "🔮 Твой выбор формирует будущее!",
    "🔥 Вперёд к новым открытиям!",
    ],
    'ky': [
        "✨ Сен тандоо жасадың! Жол улантылууда...",
        "🚀 Ар бир кадам — жаңы ачылыш!",
        "🌟 Мыкты! Алдыга жылабыз!",
        "🔮 Сенин тандооң келечекти түзүп жатат!",
        "🔥 Жаңы ачылыштарга карай алдыга!",
    ]
}

def genderize(text, gender):
    if not text:
        return ""
    # Универсальная обработка шаблонов {gender:male|муж|жен} для любого языка (в том числе кыргызского)
    def replacer(match):
        male, female = match.group(1), match.group(2)
        return female if gender == 'female' else male
    return re.sub(r'\{gender:male\|([^|]+)\|([^}]+)\}', replacer, text)

def get_scene_text(scene, scene_index=None, total_scenes=None, creative_prefix=None, gender='male'):
    title = genderize(scene.get('title', ''), gender)
    desc = genderize(scene.get('description', '') or scene.get('text', ''), gender)
    progress = ""
    if scene_index is not None and total_scenes is not None:
        bar_len = 8
        filled = int((scene_index+1) / total_scenes * bar_len)
        progress_bar = f"{'🟩'*filled}{'⬜️'*(bar_len-filled)} {scene_index+1}/{total_scenes}"
        progress = f"<b>Вопрос {scene_index+1} из {total_scenes}</b>\n{progress_bar}\n"
    # Формируем текст вариантов ответов
    options = scene.get('options', [])
    options_text = ""
    if options:
        options_text = "\n".join([
            f"<b>{i+1}.</b> {genderize(opt['text'], gender)}" for i, opt in enumerate(options)
        ])
    if title and desc:
        return f"{progress}<b>{title}</b>\n\n{desc}\n\n{options_text}"
    elif title:
        return f"{progress}<b>{title}</b>\n\n{options_text}"
    elif desc:
        return f"{progress}{desc}\n\n{options_text}"
    else:
        return f"{progress}Вопрос\n\n{options_text}"

async def send_scene(message_or_callback, scene, scene_type='main', state=None, creative_prefix=None, only_option_id=None, extra_buttons=None):
    scene_index = None
    total_scenes = None
    gender = 'male'
    if state is not None:
        data = await state.get_data()
        all_scenes = data.get('all_scenes', [])
        for idx, s in enumerate(all_scenes):
            if s['id'] == scene['id']:
                scene_index = idx
                break
        total_scenes = len(all_scenes)
        gender = data.get('gender', 'male')
    text = get_scene_text(scene, scene_index, total_scenes, gender=gender)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{i+1}. {genderize(opt['text'], gender)}", callback_data=f"{scene_type}:{scene['id']}:{opt['id']}")]
            for i, opt in enumerate(scene.get('options', []))
                if not only_option_id or str(opt['id']) == str(only_option_id)
            ] + (extra_buttons if extra_buttons else [])
    )
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message_or_callback.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.regexp(r'^(main|personal):'))
async def handle_scene_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    scene_index = data.get('scene_index', 0)
    try:
        all_scenes = data.get('all_scenes', [])
        if not all_scenes:
            await callback.message.answer("Тест был прерван. Начните заново.")
            await state.clear()
            return
        profile_scores = data.get('profile_scores', {})
        profession_scores = data.get('profession_scores', {})
        lang = data.get('lang', 'ru')
        gender = data.get('gender', 'male')
        scene_type, scene_id, option_id = callback.data.split(":", 2)
        scene_id = int(scene_id)
        scene = next((s for s in all_scenes if s['id'] == scene_id), None)
        if not scene:
            await callback.message.answer("Ошибка: сцена не найдена." if lang == 'ru' else "Ката: сцена табылган жок.")
            return
        selected_option = next((opt for opt in scene.get('options', []) if str(opt['id']) == option_id), None)
        if not selected_option:
            await callback.message.answer("Ошибка: опция не найдена." if lang == 'ru' else "Ката: опция табылган жок.")
            return
        
        # --- Показываем feedback только через alert ---
        feedback_text = selected_option.get('feedback')
        def genderize(text):
            if gender == 'female':
                return text.replace('{gender:male|ся|ась}', 'ась').replace('{gender:male||а}', 'а').replace('{gender:male||на}', 'на')
            else:
                return text.replace('{gender:male|ся|ась}', 'ся').replace('{gender:male||а}', '').replace('{gender:male||на}', '')
        feedback_text = genderize(feedback_text) if feedback_text else ''
        if feedback_text:
            await callback.answer(feedback_text, show_alert=True)
        
        # --- Накопление баллов по профилям (первые 6 сцен) ---
        if scene_type == 'main' and 'profile' in selected_option:
            profiles = selected_option['profile']
            if isinstance(profiles, list):
                for profile in profiles:
                    name = profile.get('name') if isinstance(profile, dict) else profile
                    profile_scores[name] = profile_scores.get(name, 0) + 1
            else:
                name = profiles.get('name') if isinstance(profiles, dict) else profiles
                profile_scores[name] = profile_scores.get(name, 0) + 1
        
        # --- После 6-й сцены сразу запускаем персональные сцены ---
        if scene_type == 'main' and scene_id == 5:
            if profile_scores:
                max_score = max(profile_scores.values())
                top_profiles = [k for k, v in profile_scores.items() if v == max_score]
                top_profile = random.choice(top_profiles)  # выбираем одно направление случайно из топовых
            else:
                top_profile = None
            # --- Исправленный словарь для перевода профиля на русский ---
            PROFILE_TO_PROFILE_NAME = {
                'Техническая': 'Техническая',
                'Техникалык': 'Техническая',
                'Гуманитарная': 'Гуманитарная',
                'Гуманитардык': 'Гуманитарная',
                'Естественно-научная': 'Естественно-научная',
                'Жаратылыш таануу': 'Естественно-научная',
                'Социально-экономическая': 'Социально-экономическая',
                'Социалдык-экономикалык': 'Социально-экономическая',
                'Творческо-художественная': 'Творческо-художественная',
                'Чыгармачыл-көркөм': 'Творческо-художественная',
                'Прикладно-технологическая': 'Прикладно-технологиялык',
                'Колдонмо-технологиялык': 'Прикладно-технологиялык',
            }
            profile_name = PROFILE_TO_PROFILE_NAME.get(top_profile)
            logger.info(f"[DEBUG] top_profile={top_profile}, profile_name={profile_name}")
            sm = SceneManager(language=lang, gender=gender)
            personal_scenes = sm.get_personal_scenes_by_branch(profile_name)
            logger.info(f"[DEBUG] personal_scenes count: {len(personal_scenes)}")
            if not personal_scenes:
                await callback.message.answer("Нет персональных сцен для этого профиля. Попробуйте выбрать другой." if lang == 'ru' else "Бул профиль үчүн жеке сценалар жок. Башка профилди тандап көрүңүз.")
                return
            await state.update_data(
                all_scenes=personal_scenes,
                scene_index=0,
                branch=profile_name,
                profile_scores=profile_scores,
                profession_scores=profession_scores
            )
            await send_scene(callback, personal_scenes[0], scene_type='personal', state=state)
            return
        
        # --- В персональных сценах считаем баллы по всем profiles (по name) ---
        if scene_type == 'personal' and 'profiles' in selected_option:
            for prof in selected_option['profiles']:
                prof_name = prof.get('name')
                if prof_name:
                    profession_scores[prof_name] = profession_scores.get(prof_name, 0) + prof.get('weight', 1)
        
        # --- Если персональные сцены закончились — выводим результат ---
        if scene_type == 'personal' and (scene_index+1 >= len(all_scenes)):
            logger.info(f"[DEBUG] Завершение персональных сцен: scene_index={scene_index}, len(all_scenes)={len(all_scenes)}")
            await show_test_result(callback, state)
            return
        
        # --- Переход к следующей сцене ---
        if scene_index+1 < len(all_scenes):
            await state.update_data(scene_index=scene_index+1, profile_scores=profile_scores, profession_scores=profession_scores)
            next_scene = all_scenes[scene_index+1]
            await send_scene(callback, next_scene, scene_type=scene_type, state=state)
            # --- СОХРАНЯЕМ ПРОГРЕСС ---
            await save_test_progress(
                callback.from_user.id,
                scene_index+1,
                all_scenes,
                profile_scores,
                profession_scores,
                lang
            )
        else:
            # Если вдруг вышли за пределы массива, явно вызываем show_test_result
            logger.info(f"[DEBUG] Индекс вне диапазона: scene_index={scene_index}, len(all_scenes)={len(all_scenes)}")
            await show_test_result(callback, state)
    except Exception as e:
        logger.error(f"Ошибка в handle_scene_callback: {e}")
        await state.clear()
        await callback.message.answer("Произошла ошибка. Попробуйте начать тест заново.")

async def show_test_result(message_or_callback, state: FSMContext, all_collected=False):
    logger.info("[DEBUG] show_test_result вызван")
    data = await state.get_data()
    profile_scores = data.get('profile_scores', {})
    profession_scores = data.get('profession_scores', {})
    user_id = message_or_callback.from_user.id if hasattr(message_or_callback, 'from_user') else message_or_callback.message.from_user.id
    lang = data.get('lang', 'ru')
    artifact_lang = lang
    
    # --- Локализация ключей для детализации ---
    details_keys = {
        'ru': {
            'profile_scores': 'Профильные баллы',
            'profession_scores': 'Профессиональные баллы',
            'artifact': 'Артефакт',
            'lang': 'Язык',
        },
        'ky': {
            'profile_scores': 'Профильдик упайлар',
            'profession_scores': 'Кесиптик упайлар',
            'artifact': 'Артефакт',
            'lang': 'Тил',
        }
    }[artifact_lang]
    
    # --- Вдохновляющие заголовки и фразы ---
    result_titles = {
        'ru': "<b>🎉 Твой путь только начинается!</b>",
        'ky': "<b>🎉 Сенин жолуң эми башталды!</b>"
    }
    artifact_phrases = {
        'ru': "🏆 Ты получил уникальный артефакт! Это твой символ достижений и новых открытий:",
        'ky': "🏆 Сен уникалдуу артефакт алдың! Бул сенин жетишкендиктериңдин жана жаңы ачылыштарыңдын белгиси:"
    }
    all_collected_phrases = {
        'ru': "🎊 Ты собрал все артефакты этого профиля! Ты — настоящий исследователь!",
        'ky': "🎊 Бул профилдин бардык артефакттарын чогулттуң! Сен чыныгы изилдөөчүсүң!"
    }
    no_profession_phrases = {
        'ru': "🤔 Не удалось определить профессию. Попробуй пройти тест ещё раз или выбери другой путь!",
        'ky': "🤔 Кесип аныкталган жок. Тестти кайра өтүп көр же башка жолду танда!"
    }
    top_professions_title = {
        'ru': "<b>🔝 Твои сильные стороны (ТОП-3 профессии):</b>",
        'ky': "<b>🔝 Сенин күчтүү жактарың (ТОП-3 кесип):</b>"
    }
    top_profiles_title = {
        'ru': "<b>🌈 Твои ведущие профили:</b>",
        'ky': "<b>🌈 Сенин негизги профилдериң:</b>"
    }
    details_title = {
        'ru': "<b>📊 Детализация результата:</b>",
        'ky': "<b>📊 Натыйжанын деталдары:</b>"
    }
    retry_text = {
        'ru': "🔄 Пройти тест заново",
        'ky': "🔄 Тестти кайра өтүү"
    }
    
    # --- Фильтруем только профессии, для которых есть артефакт ---
    prof_keys = set(ARTIFACTS_BY_PROFESSION.keys())
    prof_scores = {k: v for k, v in profession_scores.items() if k in prof_keys}
    
    # --- Определяем топ-3 профессии ---
    top_professions = []
    if prof_scores:
        top_professions = sorted(prof_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # --- Получаем артефакт по топ-1 профессии (если есть) ---
    top_profession = top_professions[0][0] if top_professions else None
    max_score = top_professions[0][1] if top_professions else 0
    artifact = None
    if top_profession in ARTIFACTS_BY_PROFESSION:
        artifact = ARTIFACTS_BY_PROFESSION[top_profession].get(artifact_lang) or ARTIFACTS_BY_PROFESSION[top_profession].get('ru')
    
    # --- Получаем список артефактов пользователя ---
    user = await get_user_data_from_db(user_id)
    user_artifacts = user.artifacts if user else []
    
    # --- Проверяем, есть ли этот артефакт ---
    artifact_key = artifact['name'] if artifact else None
    new_artifact = artifact_key and artifact_key not in user_artifacts
    
    # --- Сохраняем артефакт, если новый ---
    if artifact_key:
        try:
            if new_artifact:
                user_artifacts.append(artifact_key)
                user.artifacts = json.dumps(user_artifacts, ensure_ascii=False)
                allowed_fields = {
                    "telegram_id", "fio", "school", "class_number", "class_letter",
                    "gender", "birth_year", "city", "language", "artifacts", "opened_profiles"
                }
                user_data = {k: v for k, v in user.__dict__ if k in allowed_fields}
                if isinstance(user_data.get('opened_profiles'), list):
                    user_data['opened_profiles'] = json.dumps(user_data['opened_profiles'], ensure_ascii=False)
                if user_data.get('language') not in ['ru', 'ky']:
                    user_data['language'] = normalize_lang(user_data.get('language', 'ru'))
                await UserManager.update_user(user_id, **user_data)
            if new_artifact:
                await message_or_callback.answer(f"🎉 Ты получил новый артефакт: <b>{artifact_key}</b>!" if lang == 'ru' else f"🎉 Сен жаңы артефакт алдың: <b>{artifact_key}</b>!", parse_mode="HTML")
        except Exception as e:
            logger.error(f"[ERROR] Не удалось сохранить артефакт: {e}")
            await message_or_callback.answer("⚠️ Произошла ошибка при сохранении артефакта. Попробуйте позже." if lang == 'ru' else "⚠️ Артефакты сактоодо ката кетти. Кийинчерээк аракет кылып көрүңүз.")
    else:
        await message_or_callback.answer("❗️ Артефакт не определён. Попробуйте пройти тест ещё раз или выберите другой путь." if lang == 'ru' else "❗️ Артефакт аныкталган жок. Тестти кайра өтүп көрүңүз же башка жолду тандаңыз.")
    
    # --- Добавляем профиль в opened_profiles ---
    if top_profession:
        opened_profiles = set(user.opened_profiles or [])
        opened_profiles.add(top_profession)
        user.opened_profiles = list(opened_profiles)
        await UserManager.update_user(user_id, opened_profiles=user.opened_profiles)
    
    # --- КРАСИВОЕ ОФОРМЛЕНИЕ ---
    lines = []
    lines.append(result_titles[artifact_lang])
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    
    if all_collected:
        lines.append(all_collected_phrases[artifact_lang])
    elif artifact:
        lines.append(artifact_phrases[artifact_lang] + f"\n<b>{artifact['name']}</b> — <i>{artifact['desc']}</i>")
    else:
        lines.append(no_profession_phrases[artifact_lang])
    
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    
    # --- Топ-3 профессии ---
    if not profession_scores:
        lines.append(no_profession_phrases[artifact_lang])
    else:
        lines.append(top_professions_title[artifact_lang])
        for name, score in top_professions:
            display_name = PROFILE_TRANSLATIONS[artifact_lang].get(name, name)
            lines.append(f"<b>• {display_name}</b> — <b>{score} ⭐</b>")
    
    # --- Топ-3 профиля (для информации) ---
    if profile_scores:
        top_profiles = sorted(profile_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(top_profiles_title[artifact_lang])
        for name, score in top_profiles:
            display_name = PROFILE_TRANSLATIONS[artifact_lang].get(name, name)
            lines.append(f"<b>• {display_name}</b> — <b>{score} ⭐</b>")
        top_profile = top_profiles[0][0] if top_profiles else "-"
    else:
        top_profile = "-"
    
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    
    # --- Детализация (profile_scores, profession_scores, artifact, lang) ---
    details_lines = []
    details_lines.append(f"<b>• {details_keys['profile_scores']}:</b> <code>{profile_scores}</code>")
    details_lines.append(f"<b>• {details_keys['profession_scores']}:</b> <code>{profession_scores}</code>")
    details_lines.append(f"<b>• {details_keys['artifact']}:</b> <code>{artifact_key if artifact_key else '-'}</code>")
    details_lines.append(f"<b>• {details_keys['lang']}:</b> <code>{artifact_lang}</code>")
    lines.append(details_title[artifact_lang] + '\n' + '\n'.join(details_lines))
    
    text = "\n".join(lines)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=retry_text[artifact_lang], callback_data="restart_test")]
        ]
    )
    
    # Разбиваем длинные сообщения на части, если нужно
    MAX_LEN = 4000
    if isinstance(message_or_callback, Message):
        for i in range(0, len(text), MAX_LEN):
            await message_or_callback.answer(text[i:i+MAX_LEN], reply_markup=keyboard if i == 0 else None, parse_mode="HTML")
    else:
        try:
            for i in range(0, len(text), MAX_LEN):
                await message_or_callback.message.edit_text(text[i:i+MAX_LEN], reply_markup=keyboard if i == 0 else None, parse_mode="HTML")
        except Exception as e:
            logger.error(f"[DEBUG] Ошибка при отправке результата: {e}")
            if "message is not modified" in str(e):
                pass  # Просто игнорируем эту ошибку
            else:
                raise
    
    await state.clear()

    # --- Сохраняем результат теста в API (TestResult) ---
    try:
        test_result = {
            "telegram_id": user_id,
            "finished_at": datetime.now().isoformat(),
            "profile": top_profession or "-",
            "score": max_score if prof_scores else 0,
            "details": json.dumps({
                "profile_scores": profile_scores,
                "profession_scores": profession_scores,
                "artifact": artifact_key,
                "lang": artifact_lang
            }, ensure_ascii=False)
        }
        await TestResultsManager.add_test_result(test_result)
    except Exception as e:
        logger.error(f"[ERROR] Не удалось сохранить результат теста: {e}")
    # --- УДАЛЯЕМ ПРОГРЕСС ---
    await delete_test_progress(user_id)
    logger.info("[DEBUG] show_test_result завершён")

@router.callback_query(F.data == "restart_test")
async def restart_test_callback(callback: CallbackQuery, state: FSMContext):
    await start_test(callback.message, state)

@router.callback_query(F.data == "to_start")
async def to_start_callback(callback: CallbackQuery, state: FSMContext):
    # Возврат на самое начало теста
    await start_test_flow(callback.message, state)

@router.callback_query(F.data.regexp(r'^(personal):'))
async def handle_personal_scene_callback(callback: CallbackQuery, state: FSMContext):
    await handle_scene_callback(callback, state)

# --- Индивидуальные советы по профессиям ---
# Часть PROFESSION_TIPS добавлена в начало файла

@router.message(F.text.in_(["🗝️ Коллекция артефактов", "🗝️ Артефакттар коллекциясы"]))
async def show_artifact_collection(message: Message):
    user_id = message.from_user.id
    user = await get_user_data_from_db(user_id)
    lang = await get_user_lang(user_id)
    
    if not user:
        await message.answer(
            "Пожалуйста, сначала пройдите регистрацию." if lang == 'ru' else 
            "Алгач катталуудан өтүңүз.",
            parse_mode="HTML"
        )
        return
    
    try:
        # Parse artifacts from JSON string if it's a string, otherwise use empty list
        user_artifacts = json.loads(user.artifacts) if isinstance(user.artifacts, str) else (user.artifacts or [])
        user_artifacts = set(user_artifacts)
        
        artifact_lang = lang
        branch_names = {
            'ru': {
                'technical': 'Технический',
                'natural_science': 'Естественно-научный',
                'humanitarian': 'Гуманитарный',
                'social_economic': 'Социально-экономический',
                'creative_art': 'Творческо-художественный',
                'applied_technology': 'Прикладно-технологический',
            },
            'ky': {
                'technical': 'Техникалык',
                'natural_science': 'Жаратылыш таануу',
                'humanitarian': 'Гуманитардык',
                'social_economic': 'Социалдык-экономикалык',
                'creative_art': 'Творчестволук-көркөм',
                'applied_technology': 'Колдонмо-технологиялык',
            }
        }[artifact_lang]
        
        kb = InlineKeyboardBuilder()
        for branch, name in branch_names.items():
            kb.button(text=name, callback_data=f"artifact_branch:{branch}")
        kb.adjust(2)
        
        await message.answer(
            "Выберите профиль для просмотра артефактов:" if artifact_lang == 'ru' else 
            "Артефакттарды көрүү үчүн профилди тандаңыз:",
            reply_markup=kb.as_markup()
        )
    except Exception as e:
        logger.error(f"Error in show_artifact_collection: {e}")
        await message.answer(
            "Произошла ошибка при загрузке коллекции. Пожалуйста, попробуйте позже." if lang == 'ru' else
            "Коллекцияны жүктөөдө ката кетти. Кийинчерээк аракет кылып көрүңүз.",
            parse_mode="HTML"
        )

@router.callback_query(F.data.regexp(r'^artifact_branch:'))
async def show_artifacts_by_branch(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await get_user_data_from_db(user_id)
    lang = await get_user_lang(user_id)
    artifact_lang = lang
    branch = callback.data.split(':', 1)[1]
    branch_names = {
        'ru': {
            'technical': 'Технический',
            'natural_science': 'Естественно-научный',
            'humanitarian': 'Гуманитарный',
            'social_economic': 'Социально-экономический',
            'creative_art': 'Творческо-художественный',
            'applied_technology': 'Прикладно-технологический',
        },
        'ky': {
            'technical': 'Техникалык',
            'natural_science': 'Жаратылыш таануу',
            'humanitarian': 'Гуманитардык',
            'social_economic': 'Социалдык-экономикалык',
            'creative_art': 'Творчестволук-көркөм',
            'applied_technology': 'Колдонмо-технологиялык',
        }
    }[artifact_lang]
    arts = [art for art in ARTIFACTS_BY_PROFESSION.values() if art.get('branch') == branch][:10]
    total = len(arts)
    collected = sum(1 for art in arts if art.get(artifact_lang, {}).get('name', '') in user_artifacts)
    bar_len = 10
    filled = int(bar_len * collected / total) if total else 0
    progress_bar = f"{'🟩'*filled}{'⬜️'*(bar_len-filled)} {collected}/{total}"
    # --- Локализация статусов ---
    status_received = {"ru": "получен!", "ky": "алынды!"}
    status_not_received = {"ru": "ещё не получен", "ky": "азырынча алына элек"}
    lines = [f"<b>🗝️ {branch_names[branch]} профиль:</b>" if artifact_lang == 'ru' else f"<b>🗝️ {branch_names[branch]} профили:</b>", progress_bar]
    all_collected = True
    for art in arts:
        if artifact_lang in art:
            art_name = art[artifact_lang]['name']
            emoji = art[artifact_lang].get('emoji', '🗝️')
            desc = art[artifact_lang]['desc']
        else:
            art_name = art['ru']['name']
            emoji = art['ru'].get('emoji', '🗝️')
            desc = art['ru']['desc']
        if art_name in user_artifacts:
            lines.append(f"{emoji} <b>{art_name}</b> — <i>{status_received[artifact_lang]}</i>\n{desc}")
        else:
            lines.append(f"{emoji} <b>{art_name}</b> — <i>{status_not_received[artifact_lang]}</i>")
            all_collected = False
    if all_collected and arts:
        lines.append("\n🎉 <b>Поздравляем! Ты собрал все артефакты этого профиля!</b>" if artifact_lang=='ru' else "\n🎉 <b>Куттуктайбыз! Бул профилдин бардык артефакттарын чогулттуң!</b>")
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Выбрать другой профиль" if artifact_lang == 'ru' else "Башка профиль тандоо", callback_data="artifact_choose_profile")]]
    )
    await callback.message.edit_text("\n\n".join(lines), parse_mode="HTML", reply_markup=back_kb)
    await callback.answer()

@router.callback_query(F.data == "artifact_choose_profile")
async def artifact_choose_profile(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    artifact_lang = lang
    
    branch_names = {
        'ru': {
            'technical': 'Технический',
            'natural_science': 'Естественно-научный',
            'humanitarian': 'Гуманитарный',
            'social_economic': 'Социально-экономический',
            'creative_art': 'Творческо-художественный',
            'applied_technology': 'Прикладно-технологический',
        },
        'ky': {
            'technical': 'Техникалык',
            'natural_science': 'Жаратылыш таануу',
            'humanitarian': 'Гуманитардык',
            'social_economic': 'Социалдык-экономикалык',
            'creative_art': 'Творчестволук-көркөм',
            'applied_technology': 'Колдонмо-технологиялык',
        }
    }[artifact_lang]
    
    kb = InlineKeyboardBuilder()
    for branch, name in branch_names.items():
        kb.button(text=name, callback_data=f"artifact_branch:{branch}")
    kb.adjust(2)
    
    await callback.message.edit_text(
        "Выберите профиль для просмотра артефактов:" if artifact_lang == 'ru' else "Артефакттарды көрүү үчүн профилди тандаңыз:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# --- Порталы: быстрый доступ к персональным профилям ---
@router.message(F.text.in_(["🗝️ Порталы", "🗝️ Порталдар"]))
async def show_portals(message: Message):
    user_id = message.from_user.id
    user = await get_user_data_from_db(user_id)
    opened_profiles = user.opened_profiles or []
    # --- Автокоррекция: заменяем кыргызские профили на русские ---
    corrected_profiles = []
    changed = False
    for prof in opened_profiles:
        if prof in KY_TO_RU_PROFILE:
            corrected_profiles.append(KY_TO_RU_PROFILE[prof])
            changed = True
        else:
            corrected_profiles.append(prof)
    if changed:
        user.opened_profiles = corrected_profiles
        await UserManager.update_user(user_id, opened_profiles=user.opened_profiles)
        logger.info(f"[DEBUG] Исправлены opened_profiles: {corrected_profiles}")
    opened_profiles = corrected_profiles
    lang = await get_user_lang(user_id)
    artifact_lang = lang
    if not opened_profiles:
        await message.answer("У тебя пока нет открытых порталов." if artifact_lang == 'ru' else "Сенде азырынча ачык порталдар жок.")
        return
    kb = InlineKeyboardBuilder()
    for prof in opened_profiles:
        # Переводим профиль для вывода на нужном языке
        display_name = PROFILE_TRANSLATIONS[artifact_lang].get(prof, prof)
        kb.button(text=display_name, callback_data=f"portal:{prof}")
    kb.adjust(2)
    await message.answer(
        "Выбери портал для быстрого прохождения:" if artifact_lang == 'ru' else "Тез өтүү үчүн порталды тандаңыз:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.regexp(r'^portal:'))
async def start_personal_portal(callback: CallbackQuery, state: FSMContext):
    profile_name = callback.data.split(":", 1)[1]
    # --- Автокоррекция: если вдруг profile_name на кыргызском, переводим на русский ---
    if profile_name in KY_TO_RU_PROFILE:
        profile_name = KY_TO_RU_PROFILE[profile_name]
        logger.info(f"[DEBUG] Исправлен profile_name на русский: {profile_name}")
    lang = await get_user_lang(callback.from_user.id)
    artifact_lang = lang
    gender = 'male'  # Можно доработать получение пола из user_data
    sm = SceneManager(language=lang, gender=gender)
    personal_scenes = sm.get_personal_scenes_by_branch(profile_name)
    if not personal_scenes:
        await callback.message.answer("Нет персональных сцен для этого профиля." if artifact_lang == 'ru' else "Бул профиль үчүн жеке сценалар жок.")
        return
    await state.clear()
    await state.update_data(
        all_scenes=personal_scenes,
        scene_index=0,
        branch=profile_name,
        profile_scores={},
        profession_scores={}
    )
    # --- Сохраняем открытый профиль (всегда на русском) ---
    user = await get_user_data_from_db(callback.from_user.id)
    opened_profiles = set(user.opened_profiles or [])
    # --- Автокоррекция при сохранении ---
    corrected_profiles = set()
    for prof in opened_profiles:
        if prof in KY_TO_RU_PROFILE:
            corrected_profiles.add(KY_TO_RU_PROFILE[prof])
        else:
            corrected_profiles.add(prof)
    corrected_profiles.add(profile_name)
    user.opened_profiles = list(corrected_profiles)
    await UserManager.update_user(callback.from_user.id, opened_profiles=user.opened_profiles)
    await send_scene(callback, personal_scenes[0], scene_type='personal', state=state)
    await callback.answer()

def register_handlers(dispatcher):
    dispatcher.include_router(router)