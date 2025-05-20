from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from utils.states import TestStates, RegistrationStates
from utils.scene_manager import scene_manager, SceneManager
from aiogram.filters import Command
import aiohttp
from utils.messages import get_message, normalize_lang, get_user_lang
from handlers.test_utils import start_test_flow
import json
from datetime import datetime
import random
from utils.database import db
from collections import defaultdict
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import re

router = Router()

PROFILE_DESCRIPTIONS = {
    'Исследователь': 'Тебя привлекает всё неизведанное, ты любишь искать новые подходы и открывать новые знания. Ты не боишься экспериментировать.',
    'Аналитик': 'Ты любишь анализировать информацию, находить закономерности и решать сложные задачи. Тебе нравится работать с данными и делать логические выводы.',
    'Творец': 'У тебя богатое воображение и нестандартное мышление. Ты умеешь видеть красоту и создавать что-то новое.',
    'Технарь': 'Ты увлекаешься технологиями, любишь разбираться в устройствах и создавать что-то своими руками.',
    'Коммуникатор': 'Ты легко находишь общий язык с людьми, умеешь слушать и доносить свои мысли.',
    'Организатор': 'Ты умеешь планировать, распределять задачи и вести команду к цели.',
    'Визуальный художник': 'Ты видишь мир через призму цвета и формы, умеешь создавать визуальные образы.',
    'Цифровой художник': 'Ты творишь в цифровой среде, создаёшь графику, анимацию или дизайн.',
    'Писатель': 'Ты умеешь выражать мысли через слова, создавать тексты и истории.',
    'Эколог': 'Ты заботишься о природе и стремишься сделать мир чище и лучше.',
    'Ученый-естественник': 'Ты любишь исследовать законы природы и проводить эксперименты.',
    'Социолог': 'Тебе интересно, как устроено общество и как люди взаимодействуют.',
    'Историк': 'Ты любишь изучать прошлое и находить закономерности в истории.',
    'Психолог': 'Ты разбираешься в людях и их мотивах, умеешь слушать и поддерживать.',
    'Инженер-системотехник': 'Ты проектируешь сложные системы и делаешь их эффективными.',
    'Программист': 'Ты создаёшь программы и цифровые решения для разных задач.',
    'Инженер данных': 'Ты умеешь работать с большими объёмами информации и извлекать из них пользу.',
    'Робототехник': 'Ты создаёшь умные машины и автоматизируешь процессы.',
    'Инженер-конструктор': 'Ты придумываешь и собираешь новые устройства и механизмы.',
    'Электронщик': 'Ты разбираешься в электронике и любишь паять и собирать схемы.',
    'Программист-интерфейсов': 'Ты делаешь интерфейсы удобными и красивыми.',
    'Программист серверных систем': 'Ты отвечаешь за логику и надёжность серверной части.',
    'Системный инженер': 'Ты проектируешь архитектуру и инфраструктуру проектов.',
    'Организатор мероприятий': 'Ты умеешь организовывать события и объединять людей.',
    'Фасилитатор': 'Ты помогаешь команде работать эффективно и достигать целей.',
    'PR-специалист': 'Ты умеешь доносить информацию до широкой аудитории.',
    'Маркетолог': 'Ты анализируешь рынок и помогаешь продвигать продукты.',
    'Аналитик данных': 'Ты ищешь закономерности в данных и строишь прогнозы.',
    'Системный аналитик': 'Ты анализируешь процессы и предлагаешь оптимальные решения.',
    'Финансовый аналитик': 'Ты разбираешься в финансах и умеешь считать деньги.',
    'Логик': 'Ты любишь решать логические задачи и строить цепочки рассуждений.',
    'Дизайнер пространства': 'Ты создаёшь гармоничные и функциональные пространства.',
    'Исполнительский художник': 'Ты выражаешь себя через музыку, театр или выступления.'
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
    'Исследователь': ['Научный сотрудник', 'Лаборант', 'Data Scientist'],
    'Аналитик': ['Бизнес-аналитик', 'Финансовый аналитик', 'Data Analyst'],
    'Творец': ['Дизайнер', 'Архитектор', 'Креативный директор'],
    'Технарь': ['Инженер', 'Разработчик', 'Техник'],
    'Коммуникатор': ['PR-менеджер', 'Журналист', 'Учитель'],
    'Организатор': ['Менеджер проектов', 'Администратор', 'Event-менеджер'],
    'Визуальный художник': ['Художник', 'Иллюстратор', 'Декоратор'],
    'Цифровой художник': ['Графический дизайнер', '3D-аниматор', 'UI/UX дизайнер'],
    'Писатель': ['Копирайтер', 'Редактор', 'Сценарист'],
    'Эколог': ['Эколог', 'Специалист по устойчивому развитию'],
    'Ученый-естественник': ['Биолог', 'Физик', 'Химик'],
    'Социолог': ['Социолог', 'Исследователь общественного мнения'],
    'Историк': ['Историк', 'Архивист'],
    'Психолог': ['Психолог', 'Консультант'],
    'Инженер-системотехник': ['Системный инженер', 'Архитектор систем'],
    'Программист': ['Разработчик ПО', 'Web-разработчик'],
    'Инженер данных': ['Data Engineer', 'Аналитик данных'],
    'Робототехник': ['Инженер-робототехник', 'Мехатроник'],
    'Инженер-конструктор': ['Инженер-конструктор', 'Проектировщик'],
    'Электронщик': ['Инженер-электронщик', 'Схемотехник'],
    'Программист-интерфейсов': ['Frontend-разработчик', 'UI-разработчик'],
    'Программист серверных систем': ['Backend-разработчик', 'DevOps-инженер'],
    'Системный инженер': ['Системный архитектор', 'DevOps-инженер'],
    'Организатор мероприятий': ['Event-менеджер', 'Координатор проектов'],
    'Фасилитатор': ['Фасилитатор', 'Модератор'],
    'PR-специалист': ['PR-менеджер', 'Специалист по коммуникациям'],
    'Маркетолог': ['Маркетолог', 'Бренд-менеджер'],
    'Аналитик данных': ['Data Analyst', 'BI-аналитик'],
    'Системный аналитик': ['Системный аналитик', 'Бизнес-аналитик'],
    'Финансовый аналитик': ['Финансовый аналитик', 'Экономист'],
    'Логик': ['Математик', 'Разработчик алгоритмов'],
    'Дизайнер пространства': ['Дизайнер интерьера', 'Архитектор'],
    'Исполнительский художник': ['Актёр', 'Музыкант', 'Ведущий мероприятий']
}

RECOMMENDATION = (
    '✨ SkillPath рекомендует: Развивай свои сильные стороны и пробуй себя в разных направлениях. '
    'Мир профессий постоянно меняется, и твои уникальные качества могут быть востребованы в самых разных сферах!'
)

API_URL = "http://localhost:8000/users/"

# === ДОБАВЛЯЮ СЛОВАРЬ АРТЕФАКТОВ ПО ПРОФЕССИЯМ ===
ARTIFACTS_BY_PROFESSION = {
    # Гуманитарная ветка
    'Филология (языки и литература)': {
        'ru': {'name': 'Перворечь — Перо Века', 'desc': 'Перо, впитавшее кровь слов и дыхание поэзии.', 'emoji': '✨'},
        'ky': {'name': 'Алгачкы сөз — Кылым калеми', 'desc': 'Сөздүн каны менен поэзиянын демин сиңирген калем.', 'emoji': '✨'},
        'branch': 'humanitarian'
    },
    'История': {
        'ru': {'name': 'Хроносфера — Часы Разлома', 'desc': 'Часы, хранящие пыль империй и треск падений.', 'emoji': '⏳'},
        'ky': {'name': 'Хроносфера — Жарылуу сааты', 'desc': 'Империялардын чаңын жана кулаган үндү сактаган саат.', 'emoji': '⏳'},
        'branch': 'humanitarian'
    },
    'Правоведение': {
        'ru': {'name': 'Клинок Справедливости — Весы Слепой Истины', 'desc': 'Весы, отсекающие ложь от закона.', 'emoji': '⚖️'},
        'ky': {'name': 'Адилеттик кылычы — Сокур акыйкаттын таразасы', 'desc': 'Жалганды мыйзамдан бөлүп турган тараза.', 'emoji': '⚖️'},
        'branch': 'humanitarian'
    },
    'Журналистика': {
        'ru': {'name': 'Око Перекрестков — Перо-Микрофон', 'desc': 'Перо-микрофон, слышащее шум толпы и шёпот истины.', 'emoji': '📢'},
        'ky': {'name': 'Кесилиштер көзү — Микрофон-калем', 'desc': 'Калктын ызы-чууну жана акыйкаттын шыбышын уккан калем.', 'emoji': '📢'},
        'branch': 'humanitarian'
    },
    'Философия': {
        'ru': {'name': 'Логос-Сфера — Куб Парадоксов', 'desc': 'Куб, вращающийся в бездне мышления.', 'emoji': '🌀'},
        'ky': {'name': 'Логос-сфера — Парадокстар кубу', 'desc': 'Ойлонуу тереңдигинде айланган куб.', 'emoji': '🌀'},
        'branch': 'humanitarian'
    },
    'Культурология': {
        'ru': {'name': 'Лик Мира — Маска Тысячи Ликов', 'desc': 'Маска, отражающая хаос смыслов.', 'emoji': '🎭'},
        'ky': {'name': 'Дүйнө жүзү — Миң жүздүү маска', 'desc': 'Маанилердин хаосун чагылдырган маска.', 'emoji': '🎭'},
        'branch': 'humanitarian'
    },
    'Перевод и переводоведение': {
        'ru': {'name': 'Зеркало Эха — Камень Многоголосия', 'desc': 'Камень, повторяющий одно в тысяче языков.', 'emoji': '🗣️'},
        'ky': {'name': 'Жаңырык күзгүсү — Көп үндүү таш', 'desc': 'Бирди миң тилде кайталаган таш.', 'emoji': '🗣️'},
        'branch': 'humanitarian'
    },
    'Лингвистика': {
        'ru': {'name': 'Корень Глагола — Древо Языков', 'desc': 'Древо, чьи ветви шепчут на всех наречиях Земли.', 'emoji': '🔤'},
        'ky': {'name': 'Этиштин тамыры — Тилдер дарагы', 'desc': 'Бутактары жердеги бардык тилдерде шыбыраган дарак.', 'emoji': '🔤'},
        'branch': 'humanitarian'
    },
    'Теология': {
        'ru': {'name': 'Искра Завета — Перо Огня', 'desc': 'Перо, несущее свет немеркнущей веры.', 'emoji': '🕯️'},
        'ky': {'name': 'Антынын учкуну — От калеми', 'desc': 'Өчпөс ишенимдин жарыгын ала жүргөн калем.', 'emoji': '🕯️'},
        'branch': 'humanitarian'
    },
    'Социальная работа': {
        'ru': {'name': 'Сердце Путеводное — Компас Милосердия', 'desc': 'Компас, не ведающий ни севера, ни границ.', 'emoji': '💝'},
        'ky': {'name': 'Жол башчы жүрөк — Боорукердик компасы', 'desc': 'Түндүктү да, чек араларды да билбеген компас.', 'emoji': '💝'},
        'branch': 'humanitarian'
    },
    # Естественно-научная ветка
    'Биология': {
        'ru': {'name': 'Костяной гербарий', 'desc': 'Изогнутая коробка из слоновой кости мутанта, внутри которой — засушенные, но живые образцы флоры Зоны.', 'emoji': '🦴'},
        'ky': {'name': 'Сөөк гербарийи', 'desc': 'Муталанган пилдин сөөгүнөн жасалган ийилген кутуча, ичинде Зонанын флорасынын кургатылган, бирок тирүү үлгүлөрү бар.', 'emoji': '🦴'},
        'branch': 'natural_science'
    },
    'Химия': {
        'ru': {'name': 'Аурохим', 'desc': 'Фляжка из облучённого стекла, вечно наполненная голубым раствором.', 'emoji': '🧪'},
        'ky': {'name': 'Аурохим', 'desc': 'Нурданган айнектен жасалган фляжка, көк түстүү эритме менен дайыма толтурулган.', 'emoji': '🧪'},
        'branch': 'natural_science'
    },
    'Физика': {
        'ru': {'name': 'Резонатор Грома', 'desc': 'Портативная катушка с древними формулами, вырезанными на корпусе.', 'emoji': '⚡'},
        'ky': {'name': 'Дүңгүрөө резонатору', 'desc': 'Корпусунда байыркы формулалар оюп жазылган портативдүү катушка.', 'emoji': '⚡'},
        'branch': 'natural_science'
    },
    'Экология': {
        'ru': {'name': 'Корень Последнего Леса', 'desc': 'Узловатая древесная спираль, проросшая через сталь.', 'emoji': '🌱'},
        'ky': {'name': 'Акыркы токойдун тамыры', 'desc': 'Болоттун ичинен чыккан түйүндүү жыгач спирали.', 'emoji': '🌱'},
        'branch': 'natural_science'
    },
    'География': {
        'ru': {'name': 'Карта Живой Земли', 'desc': 'Кожа титана, вытравленная координатами, меняющимися при приближении к новым аномалиям.', 'emoji': '🗺️'},
        'ky': {'name': 'Тирүү Жердин картасы', 'desc': 'Жаңы аномалияларга жакындаганда өзгөрүлүүчү координаталар бар титандын териси.', 'emoji': '🗺️'},
        'branch': 'natural_science'
    },
    'Геология': {
        'ru': {'name': 'Осколок Сердца Плиты', 'desc': 'Камень, найденный на глубине 12 км, который пульсирует.', 'emoji': '🪨'},
        'ky': {'name': 'Плитанын Жүрөгүнүн сыныгы', 'desc': '12 км тереңдикте табылган, согуп турган таш.', 'emoji': '🪨'},
        'branch': 'natural_science'
    },
    'Фармация': {
        'ru': {'name': 'Ампула Ковчега', 'desc': 'Последняя сыворотка до-катастрофной эпохи.', 'emoji': '💉'},
        'ky': {'name': 'Ковчег ампуласы', 'desc': 'Катастрофага чейинки акыркы сыворотка.', 'emoji': '💉'},
        'branch': 'natural_science'
    },
    'Медицина': {
        'ru': {'name': 'Шприц Возрождения', 'desc': 'Инструмент, выкованный из титанового ребра павшего гиганта.', 'emoji': '🩺'},
        'ky': {'name': 'Жаңыруу шприци', 'desc': 'Түшкөн алптын титан кабыргасынан жасалган аспап.', 'emoji': '🩺'},
        'branch': 'natural_science'
    },
    'Ветеринария': {
        'ru': {'name': 'Зуб Древнего', 'desc': 'Клык хищника до-человеческой эпохи.', 'emoji': '🦷'},
        'ky': {'name': 'Байыркынын тиши', 'desc': 'Адамга чейинки доордун жырткычынын азуусу.', 'emoji': '🦷'},
        'branch': 'natural_science'
    },
    'Математика': {
        'ru': {'name': 'Куб Несходимости', 'desc': 'Геометрическая конструкция, нарушающая перспективу.', 'emoji': '🔲'},
        'ky': {'name': 'Туура келбөө кубу', 'desc': 'Перспективаны бузган геометриялык конструкция.', 'emoji': '🔲'},
        'branch': 'natural_science'
    },
    # Техническая ветка
    'Программная инженерия': {
        'ru': {'name': 'Чёрный кодекс Обнуления', 'desc': 'Книга в стальном переплёте, исписанная исцеляющими и разрушающими алгоритмами.', 'emoji': '📕'},
        'ky': {'name': 'Нөлдөө Кара Кодекси', 'desc': 'Болот мукабасындагы айыктыруучу жана жок кылуучу алгоритмдер менен жазылган китеп.', 'emoji': '📕'},
        'branch': 'technical'
    },
    'Информатика и вычислительная техника': {
        'ru': {'name': 'Сердце ЦП — Кремниевый Разум', 'desc': 'Пульсирующий процессор, окружённый сетью кабелей, как нейронной сетью.', 'emoji': '🖥️'},
        'ky': {'name': 'БЭнин Жүрөгү — Кремнийлик Акыл', 'desc': 'Нейрондук тармак сыяктуу кабелдердин тармагы менен курчалган согуп турган процессор.', 'emoji': '🖥️'},
        'branch': 'technical'
    },
    'Механика и машиностроение': {
        'ru': {'name': 'Ключ Гиганта', 'desc': 'Огромный, покрытый ржавчиной гаечный ключ, который может чинить любую машину.', 'emoji': '🔧'},
        'ky': {'name': 'Алптын Ачкычы', 'desc': 'Ар кандай машинаны оңдой ала турган чоң, датталган гайка ачкыч.', 'emoji': '🔧'},
        'branch': 'technical'
    },
    'Электроника и наноэлектроника': {
        'ru': {'name': 'Искровой Символ', 'desc': 'Микросхема, заключённая в стекло, испускающая вспышки энергии.', 'emoji': '💡'},
        'ky': {'name': 'Учкун Символу', 'desc': 'Айнек ичине камалган, энергия импульстарын чыгарган микросхема.', 'emoji': '💡'},
        'branch': 'technical'
    },
    'Архитектура': {
        'ru': {'name': 'Метр Молчащих Башен', 'desc': 'Линейка из окаменевшего стекла, по легенде — из руин первой башни Нового Города.', 'emoji': '📏'},
        'ky': {'name': 'Жымжырт Мунаралар Метр', 'desc': 'Жаңы Шаардын биринчи мунарасынын урандыларынан жасалган таштанган айнектен жасалган сызгыч.', 'emoji': '📏'},
        'branch': 'technical'
    },
    'Строительство': {
        'ru': {'name': 'Камень Основателя', 'desc': 'Грубый, треснувший кирпич, взятый из первого убежища, что выдержало Очищающее Пламя.', 'emoji': '🧱'},
        'ky': {'name': 'Негиздөөчүнүн Ташы', 'desc': 'Тазалоо Жалынына туруштук берген биринчи баш калкалоочу жайдан алынган бүдүр, жарака кеткен кирпич.', 'emoji': '🧱'},
        'branch': 'technical'
    },
    'Системотехника': {
        'ru': {'name': 'Консоль Единого Контроля', 'desc': 'Устройство на запястье, которое соединяется со всеми работающими машинами.', 'emoji': '🎛️'},
        'ky': {'name': 'Бирдиктүү Көзөмөл Консолу', 'desc': 'Бардык иштеп жаткан машиналар менен байланышкан билектеги түзмөк.', 'emoji': '🎛️'},
        'branch': 'technical'
    },
    'Автоматизация и управление': {
        'ru': {'name': 'Пульт Протокола Ω', 'desc': 'Потёртый блок управления с одной красной кнопкой и экраном.', 'emoji': '🔴'},
        'ky': {'name': 'Ω Протоколунун пульту', 'desc': 'Бир кызыл баскыч жана экрандуу эскирген башкаруу блогу.', 'emoji': '🔴'},
        'branch': 'technical'
    },
    'Робототехника': {
        'ru': {'name': 'Око Меха', 'desc': 'Одинокий оптический сенсор, извлечённый из павшего робота-защитника.', 'emoji': '👁️'},
        'ky': {'name': 'Механын Көзү', 'desc': 'Курулган робот-коргоочудан алынган жалгыз оптикалык сенсор.', 'emoji': '👁️'},
        'branch': 'technical'
    },
    'Авиа- и ракетостроение': {
        'ru': {'name': 'Оперение Последнего Полёта', 'desc': 'Обломок стабилизатора с последнего челнока, что покинул Землю.', 'emoji': '🛩️'},
        'ky': {'name': 'Акыркы Учуунун Канаттары', 'desc': 'Жерди таштаган акыркы челноктун стабилизаторунун сыныгы.', 'emoji': '🛩️'},
        'branch': 'technical'
    },
    # Социально-экономическая ветка
    'Экономика': {
        'ru': {'name': 'Весы Медного Изобилия', 'desc': 'Тотем в виде древних весов, на одной чаше — зерно, на другой — слиток золота.', 'emoji': '⚖️'},
        'ky': {'name': 'Жез Молчулук Таразасы', 'desc': 'Байыркы таразалар түрүндөгү тотем, бир табагында — дан, экинчисинде — алтын куймасы.', 'emoji': '⚖️'},
        'branch': 'social_economic'
    },
    'Менеджмент': {
        'ru': {'name': 'Жезл Четырёх Колонн', 'desc': 'Ритуальный жезл с гравировкой четырёх стихий: Ресурсы, Время, Люди и Цель.', 'emoji': '🪄'},
        'ky': {'name': 'Төрт Түркүк Таягы', 'desc': 'Төрт стихия оюп жазылган: Ресурстар, Убакыт, Адамдар жана Максат.', 'emoji': '🪄'},
        'branch': 'social_economic'
    },
    'Психология': {
        'ru': {'name': 'Кристалл Внутреннего Зеркала', 'desc': 'Полупрозрачный артефакт, в котором каждый видит своё отражение, но не внешнее, а душевное.', 'emoji': '🔮'},
        'ky': {'name': 'Ички Күзгү Кристаллы', 'desc': 'Жарым-жартылай ачыk артефакт, анда ар бир киши өз чагылышын көрөт, бирок сырткы эмес, ички чагылышын.', 'emoji': '🔮'},
        'branch': 'social_economic'
    },
    'Политология': {
        'ru': {'name': 'Перо Закона', 'desc': 'Символ древнего права: перо, написавшее первые слова о свободе и равенстве.', 'emoji': '🪶'},
        'ky': {'name': 'Мыйзам Канаты', 'desc': 'Байыркы укуктун символу: эркиндик жана теңдик жөнүндө биринчи сөздөрдү жазган канат.', 'emoji': '🪶'},
        'branch': 'social_economic'
    },
    'Социология': {
        'ru': {'name': 'Сеть Тысячи Голосов', 'desc': 'Ткань, сотканная из нитей, каждая из которых символизирует отдельную судьбу.', 'emoji': '🕸️'},
        'ky': {'name': 'Миң Үндүн Тору', 'desc': 'Жиптерден токулган кездеме, ар бир жиби өзүнчө тагдырды билдирет.', 'emoji': '🕸️'},
        'branch': 'social_economic'
    },
    'Бизнес-информатика': {
        'ru': {'name': 'Ядро Архитектора', 'desc': 'Светящийся куб, внутри которого движутся потоки данных, словно реки света.', 'emoji': '🧊'},
        'ky': {'name': 'Архитектордун Ядросу', 'desc': 'Ичинде маалымат агымдары суу дарыялары сыяктуу кыймылдаган жаркыраган куб.', 'emoji': '🧊'},
        'branch': 'social_economic'
    },
    'Маркетинг': {
        'ru': {'name': 'Факел Перевоплощения', 'desc': 'Огненный символ, зажигаемый при рождении идеи.', 'emoji': '🔥'},
        'ky': {'name': 'Кайра Түзүү Машаласы', 'desc': 'Идея төрөлгөндө күйүүчү отту символ.', 'emoji': '🔥'},
        'branch': 'social_economic'
    },
    'Финансы и кредит': {
        'ru': {'name': 'Монета Вечного Обмена', 'desc': 'С одной стороны — хлеб, с другой — рукопожатие.', 'emoji': '🪙'},
        'ky': {'name': 'Түбөлүк Алмашуу Монетасы', 'desc': 'Бир жагында — нан, экинчи жагында — кол алышуу.', 'emoji': '🪙'},
        'branch': 'social_economic'
    },
    'Государственное и муниципальное управление': {
        'ru': {'name': 'Ключ от Врат Города', 'desc': 'Огромный металлический ключ с резьбой в форме карт улиц.', 'emoji': '🗝️'},
        'ky': {'name': 'Шаар Дарбазасынын Ачкычы', 'desc': 'Көчө карталары формасындагы сайы бар чоң металл ачкыч.', 'emoji': '🗝️'},
        'branch': 'social_economic'
    },
    'Международные отношения': {
        'ru': {'name': 'Чаша Народов', 'desc': 'Кубок, составленный из частей десяти различных культур, инкрустированный фразами на разных языках.', 'emoji': '🏆'},
        'ky': {'name': 'Элдер Чөйчөгү', 'desc': 'Он түрдүү маданияттын бөлүктөрүнөн жасалган, ар кандай тилдерде фразалар менен инкрустацияланган кубок.', 'emoji': '🏆'},
        'branch': 'social_economic'
    },
    # Творческо-художественная ветка
    'Дизайн': {
        'ru': {'name': 'Кристалл Композиции', 'desc': 'Кристалл, грани которого отражают идеальные пропорции, цветовые гармонии и силу формы.', 'emoji': '💎'},
        'ky': {'name': 'Композиция Кристаллы', 'desc': 'Идеалдуу пропорцияларды, түстүк гармонияларды жана форманын күчүн чагылдырган кристалл.', 'emoji': '💎'},
        'branch': 'creative_art'
    },
    'Изобразительное искусство': {
        'ru': {'name': 'Первая Кисть Сотворения', 'desc': 'Кисть, вырезанная из дерева мифического леса, которой, по легенде, был нарисован первый рассвет.', 'emoji': '🖌️'},
        'ky': {'name': 'Жаратуунун Биринчи Кыл калеми', 'desc': 'Легенда боюнча, биринчи таң атууну чийген, мифтик токойдун жыгачынан жасалган кыл калем.', 'emoji': '🖌️'},
        'branch': 'creative_art'
    },
    'Музыка и музыкальное искусство': {
        'ru': {'name': 'Золотой Камертон Гармонии', 'desc': 'Камертон, который при ударе по воздуху заставляет реальность затихать.', 'emoji': '🎼'},
        'ky': {'name': 'Гармония Алтын Камертону', 'desc': 'Аба боюнча чыкканда реалдуулуkту тынчтандыруучу камертон.', 'emoji': '🎼'},
        'branch': 'creative_art'
    },
    'Архитектура и урбанистика': {
        'ru': {'name': 'Камень Основателя', 'desc': 'Блок из чистого мрамора, будто срезанный с древнего храма.', 'emoji': '🏛️'},
        'ky': {'name': 'Негиздөөчүнүн Ташы', 'desc': 'Байыркы храмдан кесилгендей таза мрамордон жасалган блок.', 'emoji': '🏛️'},
        'branch': 'creative_art'
    },
    'Актёрское мастерство': {
        'ru': {'name': 'Маска Чистой Эмоции', 'desc': 'Маска, половина которой бела, половина — чёрна, выражение которой меняется в зависимости от рук, что держат её.', 'emoji': '🎭'},
        'ky': {'name': 'Таза Эмоция Маскасы', 'desc': 'Жарымы ак, жарымы кара, кармаган колдорго жараша анын туюнтмасы өзгөргөн маска.', 'emoji': '🎭'},
        'branch': 'creative_art'
    },
    'Режиссура': {
        'ru': {'name': 'Око Великой Сцены', 'desc': 'Линза в оправе, похожей на театральный прожектор.', 'emoji': '🎥'},
        'ky': {'name': 'Улуу Сахна Көзү', 'desc': 'Театралдыk прожекторго окшош оправадагы линза.', 'emoji': '🎥'},
        'branch': 'creative_art'
    },
    'Фотография': {
        'ru': {'name': 'Объектив Времени', 'desc': 'Легендарный объектив, внутри которого вращаются образы прошедших эпох.', 'emoji': '📷'},
        'ky': {'name': 'Убакыт Объективи', 'desc': 'Ичинде өткөн доорлордун образдары айланган легендарлуu объектив.', 'emoji': '📷'},
        'branch': 'creative_art'
    },
    'Хореография': {
        'ru': {'name': 'Сандалии Ветра', 'desc': 'Танцевальная обувь, сплетённая из шелка и мифической травы.', 'emoji': '🩰'},
        'ky': {'name': 'Шамал Сандалийлери', 'desc': 'Жибек жана мифтиk чөптөн токулган бий бут кийими.', 'emoji': '🩰'},
        'branch': 'creative_art'
    },
    'Мода и текстиль': {
        'ru': {'name': 'Нить Преображения', 'desc': 'Бесконечная серебряная нить, из которой были сотканы первые образы стиля.', 'emoji': '🧵'},
        'ky': {'name': 'Кайра Түзүү Жиби', 'desc': 'Биринчи стиль образдары токулган түбөлүк күмүш жип.', 'emoji': '🧵'},
        'branch': 'creative_art'
    },
    'Арт-менеджмент': {
        'ru': {'name': 'Скипетр Вдохновения', 'desc': 'Посох, инкрустированный символами искусств: кисть, маска, камертон.', 'emoji': '🎨'},
        'ky': {'name': 'Шыктандыруу Скипетри', 'desc': 'Искусство символдору менен инкрустацияланган: кыл калем, маска, камертон.', 'emoji': '🎨'},
        'branch': 'creative_art'
    },
    # Прикладно-технологическая ветка
    'Слесарное дело': {
        'ru': {'name': 'Ключ Вечного Зазора', 'desc': 'Легендарный гаечный ключ, вручённый мастеру, чьи руки «закрутили» мост через бурную реку.', 'emoji': '🔩'},
        'ky': {'name': 'Түбөлүк Кенемте Ачкычы', 'desc': 'Колдору шаркыратманын аркылуу көпүрөгө "бурап" салган устага берилген легендалуу гайка ачкыч.', 'emoji': '🔩'},
        'branch': 'applied_technology'
    },
    'Электромонтаж': {
        'ru': {'name': 'Искра Первородной Сети', 'desc': 'Осколок первого кабеля, от которого загорелись уличные фонари.', 'emoji': '⚡'},
        'ky': {'name': 'Алгачкы Тармактын Учкуну', 'desc': 'Көчө фонарлары күйгөн биринчи кабелдин сыныгы.', 'emoji': '⚡'},
        'branch': 'applied_technology'
    },
    'Автомеханика': {
        'ru': {'name': 'Коленвал Мира', 'desc': 'Часть двигателя, запустившего первую машину великого кочевника.', 'emoji': '🚗'},
        'ky': {'name': 'Дүйнөнүн Коленвалы', 'desc': 'Улуу көчмөндүн биринчи машинасын күйгүзгөн кыймылдаткычтын бөлүгү.', 'emoji': '🚗'},
        'branch': 'applied_technology'
    },
    'Сварочные технологии': {
        'ru': {'name': 'Пламя Скрепляющего Братства', 'desc': 'Ритуальный сварочный шов, оставшийся на главной балке легендарного купола.', 'emoji': '🔥'},
        'ky': {'name': 'Биригүүчү Бир Туугандыктын Жалыны', 'desc': 'Легендалуу күмбөздүн негизги устунунда калган ритуалдык ширетүү жиги.', 'emoji': '🔥'},
        'branch': 'applied_technology'
    },
    'Токарное и фрезерное дело': {
        'ru': {'name': 'Ось Вечной Точности', 'desc': 'Сверло, выточенное вручную до абсолютной симметрии.', 'emoji': '🛠️'},
        'ky': {'name': 'Түбөлүк Тактыктын Огу', 'desc': 'Колдон толук симметрияга чейин жасалган бургу.', 'emoji': '🛠️'},
        'branch': 'applied_technology'
    },
    'Поварское дело': {
        'ru': {'name': 'Черпак Девяти Столов', 'desc': 'Деревянный половник, которым подали еду в день перемирия.', 'emoji': '🥄'},
        'ky': {'name': 'Тогуз Столдун Чөмүчү', 'desc': 'Тынчтык күнү тамак берилген жыгач чөмүч.', 'emoji': '🥄'},
        'branch': 'applied_technology'
    },
    'Техническое обслуживание транспорта': {
        'ru': {'name': 'Ремень Перехода Пути', 'desc': 'Фрагмент транспортного ремня, спасшего колонну в бурю.', 'emoji': '🚚'},
        'ky': {'name': 'Жол Өтүү Кайышы', 'desc': 'Бороондо колоннаны сактап калган транспорттук кайыштын фрагменти.', 'emoji': '🚚'},
        'branch': 'applied_technology'
    },
    'Столярное дело': {
        'ru': {'name': 'Рубанок Мудрого Строителя', 'desc': 'Инструмент, которым выровняли доски для дома вечной зимы.', 'emoji': '🪚'},
        'ky': {'name': 'Акылман Курулушчунун Рубаногу', 'desc': 'Түбөлүк кыш үйү үчүн тактайларды тегиздеген аспап.', 'emoji': '🪚'},
        'branch': 'applied_technology'
    },
    'Обслуживание зданий и сооружений': {
        'ru': {'name': 'Уровень Основателя', 'desc': 'Бронзовый строительный уровень, которым выровняли основание ратуши.', 'emoji': '📐'},
        'ky': {'name': 'Негиздөөчүнүн Деңгээли', 'desc': 'Ратушанын негизин тегиздеген колдонулган коло курулуш деңгээли.', 'emoji': '📐'},
        'branch': 'applied_technology'
    },
    'Машинист подъемных машин': {
        'ru': {'name': 'Штурвал Стального Великана', 'desc': 'Руль первого подъёмного крана, поднявшего колокол собора.', 'emoji': '⚙️'},
        'ky': {'name': 'Болот Алптын Штурвалы', 'desc': 'Собордун коңгуроосун көтөргөн биринчи көтөргүч крандын рули.', 'emoji': '⚙️'},
        'branch': 'applied_technology'
    }
}

# --- Оставляем только по 10 артефактов на каждую ветку ---
def _filter_artifacts_by_branch():
    from collections import defaultdict
    filtered = {}
    branch_count = defaultdict(int)
    for k, v in ARTIFACTS_BY_PROFESSION.items():
        branch = v.get('branch')
        if branch and branch_count[branch] < 10:
            filtered[k] = v
            branch_count[branch] += 1
    return filtered
ARTIFACTS_BY_PROFESSION = _filter_artifacts_by_branch()

async def get_user_data_from_api(telegram_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}?telegram_id={telegram_id}") as resp:
            if resp.status == 200:
                return await resp.json()
            return None

@router.message(Command("test"))
async def start_test(message: Message, state: FSMContext):
    user_data = await get_user_data_from_api(message.from_user.id)
    if not user_data or not user_data.get("fio"):
        lang = await get_user_lang(message.from_user.id)
        await message.answer(get_message("register", lang))
        await state.clear()
        await state.set_state(RegistrationStates.waiting_for_fio)
        await message.answer(get_message("registration_fio", lang))
        return
    await start_test_flow(message, state)

@router.message(F.text == "🧩 Тест")
async def start_test_button(message: Message, state: FSMContext):
    await start_test(message, state)

import random

CREATIVE_TEXTS = [
    "✨ Ты сделал выбор! Путь продолжается...",
    "🚀 Каждый шаг — это новое открытие!",
    "🌟 Отлично! Двигаемся дальше!",
    "🔮 Твой выбор формирует будущее!",
    "🔥 Вперёд к новым открытиям!",
]

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
    all_scenes = data.get('all_scenes', [])
    scene_index = data.get('scene_index', 0)
    profile_scores = data.get('profile_scores', {})
    profession_scores = data.get('profession_scores', {})
    lang = data.get('lang', 'ru')
    gender = data.get('gender', 'male')
    scene_type, scene_id, option_id = callback.data.split(":", 2)
    scene_id = int(scene_id)
    scene = next((s for s in all_scenes if s['id'] == scene_id), None)
    if not scene:
        await callback.message.answer("Ошибка: сцена не найдена.")
        return
    selected_option = next((opt for opt in scene.get('options', []) if str(opt['id']) == option_id), None)
    if not selected_option:
        await callback.message.answer("Ошибка: опция не найдена.")
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
    if scene_type == 'main' and scene_index == 5:
        if profile_scores:
            top_profile = max(profile_scores.items(), key=lambda x: x[1])[0]
        else:
            top_profile = None
        PROFILE_TO_PROFILE_NAME = {
            'Техническая': 'Техническая',
            'Техникалык': 'Техническая',
            'Гуманитарная': 'Гуманитарная',
            'Гуманитардык': 'Гуманитарная',
            'Естественно-научная': 'Естественно-научная',
            'Табигый-илимий': 'Естественно-научная',
            'Социально-экономическая': 'Социально-экономическая',
            'Социалдык-экономикалык': 'Социально-экономическая',
            'Творческо-художественная': 'Творческо-художественная',
            'Чыгармачыл-көркөм': 'Творческо-художественная',
            'Прикладно-технологическая': 'Прикладно-технологическая',
            'Колдонмо-технологиялык': 'Прикладно-технологическая',
        }
        profile_name = PROFILE_TO_PROFILE_NAME.get(top_profile)
        sm = SceneManager(language=lang, gender=gender)
        personal_scenes = sm.get_personal_scenes_by_branch(profile_name)
        if not personal_scenes:
            await callback.message.answer("Нет персональных сцен для этого профиля. Попробуйте выбрать другой.")
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
    if scene_type == 'personal' and scene_index+1 >= len(all_scenes):
        await show_test_result(callback, state)
        return
    
    # --- Переход к следующей сцене ---
    await state.update_data(scene_index=scene_index+1, profile_scores=profile_scores, profession_scores=profession_scores)
    next_scene = all_scenes[scene_index+1]
    await send_scene(callback, next_scene, scene_type=scene_type, state=state)

async def show_test_result(message_or_callback, state: FSMContext, all_collected=False):
    data = await state.get_data()
    profile_scores = data.get('profile_scores', {})
    profession_scores = data.get('profession_scores', {})
    user_id = message_or_callback.from_user.id if hasattr(message_or_callback, 'from_user') else message_or_callback.message.from_user.id
    lang = data.get('lang', 'ru')
    API_USER = "http://localhost:8000/users/"
    
    # --- Фильтруем только профессии, для которых есть артефакт ---
    prof_keys = set(ARTIFACTS_BY_PROFESSION.keys())
    prof_scores = {k: v for k, v in profession_scores.items() if k in prof_keys}
    
    # --- Определяем топ-1 профессию (или случайно из топовых) ---
    top_profession = None
    if prof_scores:
        max_score = max(prof_scores.values())
        top_professions = [k for k, v in prof_scores.items() if v == max_score]
        top_profession = random.choice(top_professions)
    
    # --- Получаем артефакт по профессии и языку ---
    artifact = None
    if top_profession in ARTIFACTS_BY_PROFESSION:
        artifact = ARTIFACTS_BY_PROFESSION[top_profession].get(lang) or ARTIFACTS_BY_PROFESSION[top_profession].get('ru')
    
    # --- Получаем список артефактов пользователя ---
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_USER}?telegram_id={user_id}") as resp:
                user = await resp.json() if resp.status == 200 else {}
    except Exception as e:
        user = {}
        print(f"[ERROR] Не удалось получить пользователя из API: {e}")
    
    user_artifacts = user.get('artifacts', []) if user else []
    
    # --- Проверяем, есть ли этот артефакт ---
    artifact_key = artifact['name'] if artifact else None
    new_artifact = artifact_key and artifact_key not in user_artifacts
    
    # --- Сохраняем артефакт, если новый ---
    if artifact_key:
        try:
            if new_artifact:
                user_artifacts.append(artifact_key)
                user['artifacts'] = user_artifacts
                async with aiohttp.ClientSession() as session:
                    await session.post(API_USER, json=user)
            
            # Сохраняем в локальную базу
            db_data = db._read_db()
            user_data = db_data.get('users', {}).get(str(user_id), {})
            artifacts = set(user_data.get('artifacts', []))
            artifacts.add(artifact_key)
            user_data['artifacts'] = list(artifacts)
            db_data['users'][str(user_id)] = user_data
            db._write_db(db_data)
            
            if new_artifact:
                await message_or_callback.answer(f"🎉 Ты получил новый артефакт: <b>{artifact_key}</b>!", parse_mode="HTML")
        except Exception as e:
            print(f"[ERROR] Не удалось сохранить артефакт: {e}")
            await message_or_callback.answer("⚠️ Произошла ошибка при сохранении артефакта. Попробуйте позже.")
    else:
        await message_or_callback.answer("❗️ Артефакт не определён. Попробуйте пройти тест ещё раз или выберите другой путь.")
    
    # --- КРАСИВОЕ ОФОРМЛЕНИЕ ---
    lines = []
    lines.append(get_message("test_result_title", lang))
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    
    if all_collected:
        lines.append(get_message("test_result_all_collected", lang))
    elif artifact:
        lines.append(get_message("test_result_artifact", lang) + f" <i>{artifact['name']}</i>\n{artifact['desc']}")
    else:
        lines.append(get_message("test_result_no_profession", lang))
    
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    
    # --- Топ-3 профессии ---
    if not profession_scores:
        lines.append(get_message("test_result_no_profession", lang))
    else:
        top_professions = sorted(profession_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(get_message("test_result_top_professions", lang))
        for name, score in top_professions:
            lines.append(f"<b>{name}</b> — <b>{score} {get_message('test_result_points', lang)}</b>")
    
    # --- Топ-3 профиля (для информации) ---
    if profile_scores:
        top_profiles = sorted(profile_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append("\n" + get_message("test_result_top_profiles", lang))
        for name, score in top_profiles:
            lines.append(f"<b>{name}</b> — <b>{score} {get_message('test_result_points', lang)}</b>")
        # Определяем top_profile для дальнейшего использования
        top_profile = top_profiles[0][0] if top_profiles else "-"
    else:
        top_profile = "-"
    
    lines.append("<b>━━━━━━━━━━━━━━━━━━━━━━</b>")
    text = "\n".join(lines)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_message("test_result_retry", lang), callback_data="restart_test")]
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
            if "message is not modified" in str(e):
                pass  # Просто игнорируем эту ошибку
            else:
                raise
    
    await state.clear()

    # --- Сохраняем результат теста в API (TestResult) ---
    try:
        API_TEST_RESULT = "http://localhost:8000/test_results/"
        test_result = {
            "telegram_id": user_id,
            "finished_at": datetime.now().isoformat(),
            "profile": top_profession or "-",
            "score": max_score if prof_scores else 0,
            "details": json.dumps({
                "profile_scores": profile_scores,
                "profession_scores": profession_scores,
                "artifact": artifact_key,
                "lang": lang
            }, ensure_ascii=False)
        }
        async with aiohttp.ClientSession() as session:
            await session.post(API_TEST_RESULT, json=test_result)
    except Exception as e:
        print(f"[ERROR] Не удалось сохранить результат теста: {e}")

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
PROFESSION_TIPS = {
    'Биолог': 'Продолжай исследовать природу и не бойся задавать вопросы о мире вокруг! Твои открытия могут изменить будущее.',
    'Программист': 'Развивай навыки логики и креативности — твои идеи способны создавать новые цифровые миры!',
    'Инженер': 'Твоя страсть к созданию и улучшению вещей — твой главный инструмент. Не останавливайся на достигнутом!',
    'Физик': 'Твои эксперименты и наблюдения — ключ к разгадке тайн Вселенной. Не бойся ошибаться!',
    'Эколог': 'Ты можешь сделать мир чище и лучше. Защищай природу и вдохновляй других!',
    'Математик': 'Твои аналитические способности открывают двери в любые сферы. Не бойся сложных задач!',
    'Ветеринария': 'Твоя забота о животных делает этот мир добрее. Продолжай помогать тем, кто не может сказать спасибо!',
    'Медик': 'Твоя эмпатия и знания спасают жизни. Не забывай заботиться и о себе!',
    'Географ': 'Ты видишь мир шире других. Путешествуй, исследуй и делись открытиями!',
    'Геолог': 'Ты умеешь находить ценное даже в самом обычном. Продолжай копать глубже!',
    'Фармацевт': 'Твои знания — ключ к здоровью многих людей. Продолжай учиться и помогать!',
    # ... добавить советы для всех профессий ...
}

# 3. Коллекция артефактов (отдельное меню)
@router.message(F.text == "🗝️ Коллекция артефактов")
async def show_artifact_collection(message: Message):
    from utils.database import db
    user_id = message.from_user.id
    db_data = db._read_db()
    user_data = db_data.get('users', {}).get(str(user_id), {})
    user_artifacts = set(user_data.get('artifacts', []))
    lang = await get_user_lang(user_id)
    
    # --- Словарь веток и их названий ---
    branch_names = {
        'ru': {
            'technical': 'Технический',
            'natural_science': 'Естественно-научный',
            'humanitarian': 'Гуманитарный',
            'social_economic': 'Социально-экономический',
            'creative_art': 'Творческо-художественный',
            'applied_technology': 'Прикладно-технологический',
        },
        'kg': {
            'technical': 'Техникалык',
            'natural_science': 'Жаратылыш таануу',
            'humanitarian': 'Гуманитардык',
            'social_economic': 'Социалдык-экономикалык',
            'creative_art': 'Творчестволук-өнөр',
            'applied_technology': 'Колдонмо-технологиялык',
        }
    }[lang]
    
    # --- Клавиатура выбора профиля ---
    kb = InlineKeyboardBuilder()
    for branch, name in branch_names.items():
        kb.button(text=name, callback_data=f"artifact_branch:{branch}")
    kb.adjust(2)
    
    await message.answer(
        "Выберите профиль для просмотра артефактов:" if lang == 'ru' else "Профилди тандаңыз:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.regexp(r'^artifact_branch:'))
async def show_artifacts_by_branch(callback: CallbackQuery):
    from utils.database import db
    user_id = callback.from_user.id
    db_data = db._read_db()
    user_data = db_data.get('users', {}).get(str(user_id), {})
    user_artifacts = set(user_data.get('artifacts', []))
    lang = await get_user_lang(user_id)
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
        'kg': {
            'technical': 'Техникалык',
            'natural_science': 'Жаратылыш таануу',
            'humanitarian': 'Гуманитардык',
            'social_economic': 'Социалдык-экономикалык',
            'creative_art': 'Творчестволук-өнөр',
            'applied_technology': 'Колдонмо-технологиялык',
        }
    }[lang]
    
    # --- Новый способ: фильтруем по branch и ограничиваем 10 ---
    arts = [art for art in ARTIFACTS_BY_PROFESSION.values() if art.get('branch') == branch][:10]
    total = len(arts)
    collected = sum(1 for art in arts if art[lang]['name'] in user_artifacts)
    
    bar_len = 10
    filled = int(bar_len * collected / total) if total else 0
    progress_bar = f"{'🟩'*filled}{'⬜️'*(bar_len-filled)} {collected}/{total}"
    
    lines = [f"<b>🗝️ {branch_names[branch]} профиль:</b>", progress_bar]
    
    all_collected = True
    for art in arts:
        art_name = art[lang]['name'] if lang in art else art['ru']['name']
        # Исправлено: emoji строго из словаря, если нет — дефолт по ветке
        emoji = art[lang].get('emoji') or art['ru'].get('emoji') or {
            'technical': '⚙️',
            'natural_science': '🔬',
            'humanitarian': '📜',
            'social_economic': '💰',
            'creative_art': '🎨',
            'applied_technology': '🛠️',
        }.get(branch, '🗝️')
        desc = art[lang]['desc'] if lang in art else art['ru']['desc']
        
        if art_name in user_artifacts:
            lines.append(f"{emoji} <b>{art_name}</b> — <i>получен!</i>\n{desc}")
        else:
            lines.append(f"{emoji} <b>{art_name}</b> — <i>ещё не получен</i>")
            all_collected = False
    
    if all_collected and arts:
        lines.append("\n🎉 <b>Поздравляем! Ты собрал все артефакты этого профиля!</b>" if lang=='ru' else "\n🎉 <b>Куттуктайбыз! Бул профилдин бардык артефакттарын чогулттуң!</b>")
    
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Выбрать другой профиль" if lang == 'ru' else "Башка профиль", callback_data="artifact_choose_profile")]]
    )
    
    await callback.message.edit_text("\n\n".join(lines), parse_mode="HTML", reply_markup=back_kb)
    await callback.answer()

@router.callback_query(F.data == "artifact_choose_profile")
async def artifact_choose_profile(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    
    branch_names = {
        'ru': {
            'technical': 'Технический',
            'natural_science': 'Естественно-научный',
            'humanitarian': 'Гуманитарный',
            'social_economic': 'Социально-экономический',
            'creative_art': 'Творческо-художественный',
            'applied_technology': 'Прикладно-технологический',
        },
        'kg': {
            'technical': 'Техникалык',
            'natural_science': 'Жаратылыш таануу',
            'humanitarian': 'Гуманитардык',
            'social_economic': 'Социалдык-экономикалык',
            'creative_art': 'Творчестволук-өнөр',
            'applied_technology': 'Колдонмо-технологиялык',
        }
    }[lang]
    
    kb = InlineKeyboardBuilder()
    for branch, name in branch_names.items():
        kb.button(text=name, callback_data=f"artifact_branch:{branch}")
    kb.adjust(2)
    
    await callback.message.edit_text(
        "Выберите профиль для просмотра артефактов:" if lang == 'ru' else "Профилди тандаңыз:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# --- Порталы: быстрый доступ к персональным профилям ---
@router.message(F.text.in_(["🗝️ Порталы", "🗝️ Порталдар"]))
async def show_portals(message: Message):
    from utils.database import db
    user_id = message.from_user.id
    db_data = db._read_db()
    user_data = db_data.get('users', {}).get(str(user_id), {})
    opened_profiles = user_data.get('opened_profiles', [])
    lang = await get_user_lang(user_id)
    if not opened_profiles:
        await message.answer("У тебя пока нет открытых порталов." if lang == 'ru' else "Сизде азырынча ачык порталдар жок.")
        return

    profile_names = {
        'Техническая': '⚙️ Техникалык',
        'Гуманитарная': '📜 Гуманитардык',
        'Естественно-научная': '🔬 Жаратылыш таануу',
        'Социально-экономическая': '💼 Социалдык-экономикалык',
        'Творческо-художественная': '🎨 Творчестволук-өнөр',
        'Прикладно-технологическая': '🛠️ Колдонмо-технологиялык',
    }
    kb = InlineKeyboardBuilder()
    for prof in opened_profiles:
        text = profile_names.get(prof, prof)
        kb.button(text=text, callback_data=f"portal:{prof}")
    kb.adjust(2)
    await message.answer(
        "Выбери портал для быстрого прохождения:" if lang == 'ru' else "Порталды тандаңыз:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.regexp(r'^portal:'))
async def start_personal_portal(callback: CallbackQuery, state: FSMContext):
    profile_name = callback.data.split(":", 1)[1]
    lang = await get_user_lang(callback.from_user.id)
    gender = 'male'  # Можно доработать получение пола из user_data
    sm = SceneManager(language=lang, gender=gender)
    personal_scenes = sm.get_personal_scenes_by_branch(profile_name)
    if not personal_scenes:
        await callback.message.answer("Нет персональных сцен для этого профиля." if lang == 'ru' else "Бул профил үчүн жеке сценалар жок.")
        return
    await state.clear()
    await state.update_data(
        all_scenes=personal_scenes,
        scene_index=0,
        branch=profile_name,
        profile_scores={},
        profession_scores={}
    )
    await send_scene(callback, personal_scenes[0], scene_type='personal', state=state)
    await callback.answer()

# --- ДОПОЛНИТЕЛЬНО: сохраняем открытые профили при открытии портала после 6-й сцены ---
# Найди участок, где после 6-й сцены определяется profile_name и запускаются персональные сцены:
# После строки: await state.update_data(...)
# Добавь:
    # --- Сохраняем открытый профиль ---
    from utils.database import db
    db_data = db._read_db()
    user_data = db_data.get('users', {}).get(str(callback.from_user.id), {})
    opened_profiles = set(user_data.get('opened_profiles', []))
    opened_profiles.add(profile_name)
    user_data['opened_profiles'] = list(opened_profiles)
    db_data['users'][str(callback.from_user.id)] = user_data
    db._write_db(db_data)

def register_handlers(dispatcher):
    dispatcher.include_router(router)