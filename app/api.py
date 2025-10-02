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
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                age INTEGER NOT NULL
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
def create_animal(animal: Animal):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO animals (name, species, age) VALUES (?, ?, ?)",
                (animal.name, animal.species, animal.age)
            )
            conn.commit()
            return {"status": "success", "message": "Animal added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Обновить животное
@router.put("/{animal_id}", response_model=Animal)
def update_animal(animal_id: int, updated_animal: Animal):
    result = query_db("SELECT * FROM animals WHERE id=?", (animal_id,), one=True)
    if not result:
        raise HTTPException(status_code=404, detail="Животное не найдено")

    query_db("UPDATE animals SET name=?, species=?, age=? WHERE id=?",
             (updated_animal.name, updated_animal.species, updated_animal.age, animal_id))
    return get_animal(animal_id)


# Удалить животное
@router.delete("/{animal_id}", response_model=dict)
def delete_animal(animal_id: int):
    result = query_db("SELECT * FROM animals WHERE id=?", (animal_id,), one=True)
    if not result:
        raise HTTPException(status_code=404, detail="Животное не найдено")

    query_db("DELETE FROM animals WHERE id=?", (animal_id,))
    return {"message": "Животное удалено"}
