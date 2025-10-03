import sqlite3
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

# Импорт моделей
from models import Animal

# Создание роутера
router = APIRouter(prefix="/animals", tags=["Animals"])

# Путь к SQLite-базе данных
DB_PATH = "./database/animals.db"


def get_db():
    """Возвращает соединение с SQLite-базой"""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Инициализирует базу данных (создаёт таблицу)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                yes INTEGER,
                no INTEGER
            )
        ''')
        conn.commit()


# Инициализация базы данных при запуске
init_db()


def query_db(query: str, args: tuple = (), one: bool = False):
    """Помощник для выполнения SQL-запросов"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        result = cursor.fetchall()
        if one:
            return result[0] if result else None
        return result


# Получаем все животные
@router.get("/", response_model=list)
def get_animals():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM animals")
            rows = cursor.fetchall()

            # Преобразуем строки в словари (если хотите использовать имя столбцов)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Получить животное по ID
@router.get("/{animal_id}", response_model=Animal)
def get_animal(animal_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM animals WHERE id=?", (animal_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Animal not found")

            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Добавить животное
@router.post("/", response_model=Animal)
def add_question(animal: Animal, answer: str = "yes", parent_id: int = -1) -> Animal:

    if answer not in ("yes", "no"):
        raise ValueError("answer must be 'yes' or 'no'")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO animals (question, yes, no) VALUES (?, ?, ?)",
                (animal.question, None, None)
            )
            
            new_id = cursor.lastrowid

            if parent_id != -1:
                conn.execute(
                    f"UPDATE animals SET {answer} = ? WHERE id = ?",
                    (new_id, parent_id)
                )
                
            conn.commit()

            row = conn.execute(
                "SELECT * FROM animals WHERE id = ?",
                (new_id,)
            ).fetchone()

            return Animal(**dict(row))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Обновить животное
@router.put("/{animal_id}", response_model=Animal)
def update_animal(animal_id: int, updated_animal: Animal):
    result = query_db("SELECT * FROM animals WHERE id=?", (animal_id,), one=True)
    if not result:
        raise HTTPException(status_code=404, detail="Животное не найдено")

    query_db("UPDATE animals SET question=?, yes=?, no=? WHERE id=?",
             (updated_animal.question, updated_animal.yes, updated_animal.no, animal_id))
    return get_animal(animal_id)


# Удалить животное
@router.delete("/{animal_id}", response_model=dict)
def delete_animal(animal_id: int):
    result = query_db("SELECT * FROM animals WHERE id=?", (animal_id,), one=True)
    if not result:
        raise HTTPException(status_code=404, detail="Животное не найдено")

    query_db("DELETE FROM animals WHERE id=?", (animal_id,))
    return {"message": "Животное удалено"}
