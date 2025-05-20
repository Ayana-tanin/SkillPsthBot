from utils.scene_manager import SceneManager
from utils.states import TestStates
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from utils.messages import get_user_lang, normalize_lang
import aiohttp

async def get_user_data_from_api(telegram_id: int):
    API_URL = "http://localhost:8000/users/"
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}?telegram_id={telegram_id}") as resp:
            if resp.status == 200:
                return await resp.json()
            return None

async def start_test_flow(message: Message, state: FSMContext):
    await state.clear()
    # Получаем язык и пол пользователя
    user_data = await get_user_data_from_api(message.from_user.id)
    lang = normalize_lang(user_data.get("language", "ru")) if user_data else "ru"
    gender = user_data.get("gender", "male") if user_data else "male"
    scene_manager = SceneManager(language=lang, gender=gender)
    # Формируем маршрут: 6 базовых сцен + сцена артефакта (id=7)
    basic_scenes = scene_manager.get_basic_scenes()
    artifact_scene = scene_manager.get_scene_by_id(7)
    all_scenes = basic_scenes.copy()
    if artifact_scene:
        all_scenes.append(artifact_scene)
    # Сохраняем только первые 6 + артефакт, персональные добавим после 7-й сцены
    await state.update_data(
        scene_index=0,
        answers=[],
        profile_scores={},
        all_scenes=all_scenes,
        lang=lang,
        gender=gender,
        scene_manager_params={"language": lang, "gender": gender}
    )
    # Удаляем reply-клавиатуру при старте теста
    # await message.answer("Тест начинается!", reply_markup=ReplyKeyboardRemove())
    # Импортируем send_scene только здесь, чтобы избежать циклических импортов
    from handlers.test import send_scene
    await state.set_state(TestStates.main_scene)
    await send_scene(message, all_scenes[0], scene_type='main') 