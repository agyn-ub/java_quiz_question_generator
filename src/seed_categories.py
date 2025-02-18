from database import Database
from sqlalchemy import text
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

JAVA_CATEGORIES = [
    {
        "name": "Java Basics",
        "name_ru": "Основы Java",
        "slug": "java-basics",
    },
    {
        "name": "Object-Oriented Programming",
        "name_ru": "Объектно-ориентированное программирование",
        "slug": "oop",
    },
    {
        "name": "Classes and Objects",
        "name_ru": "Классы и Объекты",
        "slug": "classes-and-objects",
    },
    {
        "name": "Collections Framework",
        "name_ru": "Коллекции",
        "slug": "collections",
    },
    {
        "name": "Multithreading",
        "name_ru": "Многопоточность",
        "slug": "multithreading",
    },
    # {
    #     "name": "Error Handling",
    #     "name_ru": "Обработка Исключений",
    #     "slug": "error-handling",
    # },
    # {
    #     "name": "File I/O",
    #     "name_ru": "Работа с Файлами",
    #     "slug": "file-io",
    # },
    # {
    #     "name": "Generics",
    #     "name_ru": "Дженерики",
    #     "slug": "generics",
    # },
    # {
    #     "name": "Lambda Expressions",
    #     "name_ru": "Лямбда-выражения",
    #     "slug": "lambda-expressions",
    # },
    # {
    #     "name": "Stream API",
    #     "name_ru": "Stream API",
    #     "slug": "stream-api",
    # },
    # {
    #     "name": "Design Patterns",
    #     "name_ru": "Паттерны Проектирования",
    #     "slug": "design-patterns",
    # },
    # {
    #     "name": "Unit Testing",
    #     "name_ru": "Модульное Тестирование",
    #     "slug": "unit-testing",
    # },
    # {
    #     "name": "Interfaces and Abstract Classes",
    #     "name_ru": "Интерфейсы и Абстрактные Классы",
    #     "slug": "interfaces-abstract-classes",
    # },
    # {
    #     "name": "Serialization",
    #     "name_ru": "Сериализация",
    #     "slug": "serialization",
    # },
    # {
    #     "name": "Annotations",
    #     "name_ru": "Аннотации",
    #     "slug": "annotations",
    # },
    # {
    #     "name": "Reflection",
    #     "name_ru": "Рефлексия",
    #     "slug": "reflection",
    # }
]

def seed_categories(db: Database) -> None:
    """Seed the categories table with Java learning topics"""
    try:
        with db.engine.begin() as connection:
            # First, check which categories already exist
            existing = connection.execute(
                text("SELECT slug FROM categories")
            ).fetchall()
            existing_slugs = {row[0] for row in existing}
            
            # Insert only new categories
            for category in JAVA_CATEGORIES:
                if category["slug"] not in existing_slugs:
                    connection.execute(
                        text("""
                            INSERT INTO categories (name, name_ru, slug)
                            VALUES (:name, :name_ru, :slug)
                        """),
                        category
                    )
                    logger.info(f"Added category: {category['name']} ({category['name_ru']})")
                else:
                    logger.info(f"Category already exists: {category['name']}")
                    
        logger.info("Categories seeding completed successfully")
    except Exception as e:
        logger.error(f"Error seeding categories: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = Database()
    seed_categories(db) 