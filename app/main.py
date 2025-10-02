from fastapi import FastAPI
from api import router as animals_router
import uvicorn

# Создание экземпляра FastAPI приложения
app = FastAPI(
    title="Животный Акинатор",
    description="Игра для угадывания животных с использованием дерева вопросов",
    version="1.0.0"
)

# Регистрация роутера из api.py
app.include_router(animals_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
