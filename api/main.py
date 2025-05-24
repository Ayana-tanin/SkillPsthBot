from fastapi import FastAPI, Query
from .models import User, TestResult, TestProgress
from .db import get_connection, init_database
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения."""
    try:
        init_database()
        logger.info("База данных инициализирована при запуске")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise

@app.post("/users/")
def create_or_update_user(user: User):
    conn = get_connection()
    cursor = conn.cursor()
    # Сериализация полей
    user_dict = user.dict()
    for field in ["artifacts", "opened_profiles"]:
        if isinstance(user_dict.get(field), list):
            user_dict[field] = json.dumps(user_dict[field], ensure_ascii=False)
        elif user_dict.get(field) is None:
            user_dict[field] = json.dumps([])
    cursor.execute("""
        INSERT INTO users (telegram_id, fio, school, class_number, class_letter, gender, birth_year, city, language, artifacts, opened_profiles)
        VALUES (%(telegram_id)s, %(fio)s, %(school)s, %(class_number)s, %(class_letter)s, %(gender)s, %(birth_year)s, %(city)s, %(language)s, %(artifacts)s, %(opened_profiles)s)
        ON DUPLICATE KEY UPDATE fio=VALUES(fio), school=VALUES(school), class_number=VALUES(class_number), class_letter=VALUES(class_letter), gender=VALUES(gender), birth_year=VALUES(birth_year), city=VALUES(city), language=VALUES(language), artifacts=VALUES(artifacts), opened_profiles=VALUES(opened_profiles)
    """, user_dict)
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@app.get("/users/")
def get_user(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    if user:
        for field in ["artifacts", "opened_profiles"]:
            try:
                user[field] = json.loads(user[field]) if user[field] else []
            except Exception:
                user[field] = []
    cursor.close()
    conn.close()
    return user or {}

@app.post("/test_results/")
def save_test_result(result: TestResult):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO test_results (telegram_id, finished_at, profile, score, details)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (result.telegram_id, result.finished_at, result.profile, result.score, result.details)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@app.get("/test_results/")
def get_test_results(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test_results WHERE telegram_id = %s ORDER BY finished_at DESC", (telegram_id,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

@app.post("/test_progress/")
def save_test_progress(progress: TestProgress):
    conn = get_connection()
    cursor = conn.cursor()
    # Проверяем, есть ли уже прогресс для этого пользователя
    cursor.execute("SELECT id FROM test_progress WHERE telegram_id=%s", (progress.telegram_id,))
    row = cursor.fetchone()
    if row:
        # Обновляем
        cursor.execute(
            """
            UPDATE test_progress SET current_scene=%s, all_scenes=%s, profile_scores=%s, profession_scores=%s, lang=%s, updated_at=NOW()
            WHERE telegram_id=%s
            """,
            (
                progress.current_scene,
                progress.all_scenes,
                progress.profile_scores,
                progress.profession_scores,
                progress.lang,
                progress.telegram_id
            )
        )
    else:
        # Вставляем
        cursor.execute(
            """
            INSERT INTO test_progress (telegram_id, current_scene, all_scenes, profile_scores, profession_scores, lang, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                progress.telegram_id,
                progress.current_scene,
                progress.all_scenes,
                progress.profile_scores,
                progress.profession_scores,
                progress.lang
            )
        )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "ok"}

@app.get("/test_progress/")
def get_test_progress(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test_progress WHERE telegram_id=%s", (telegram_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return row
    return {}

@app.delete("/test_progress/")
def delete_test_progress(telegram_id: int = Query(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_progress WHERE telegram_id=%s", (telegram_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}