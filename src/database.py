from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        logger.info(f"Connecting to database with URL: {DATABASE_URL}")
        self.engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )
    
    def get_categories(self) -> List[Dict]:
        """Get all categories from the database"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT id, name, name_ru, slug FROM categories"))
                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "name_ru": row[2],
                        "slug": row[3]
                    } for row in result
                ]
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    def get_existing_questions(self, category_id: int) -> List[Dict]:
        """Get existing questions for a specific category"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("""
                        SELECT question, correct_answer, options, difficulty, score 
                        FROM quiz_questions 
                        WHERE category_id = :category_id
                    """),
                    {"category_id": category_id}
                )
                return [
                    {
                        "question": row[0],
                        "correct_answer": row[1],
                        "options": row[2],
                        "difficulty": row[3],
                        "score": row[4]
                    } for row in result
                ]
        except Exception as e:
            logger.error(f"Error getting questions for category {category_id}: {e}")
            return []

    def insert_question(self, question_data: Dict, category_id: int) -> bool:
        """Insert a new question into the database"""
        try:
            with self.engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO quiz_questions 
                        (category_id, question, correct_answer, options, difficulty, score) 
                        VALUES (:category_id, :question, :correct_answer, :options, :difficulty, :score)
                    """),
                    {
                        "category_id": category_id,
                        "question": question_data["question"],
                        "correct_answer": question_data["correct_answer"],
                        "options": question_data["options"],
                        "difficulty": question_data.get("difficulty", "medium"),
                        "score": question_data.get("score", 5)
                    }
                )
            return True
        except Exception as e:
            logger.error(f"Error inserting question for category {category_id}: {e}")
            return False

    def save_user_score(self, user_id: int, category_id: int, score: int, correct_answers: int) -> bool:
        """Save user's quiz score"""
        try:
            with self.engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO user_scores 
                        (user_id, category_id, score, correct_answers) 
                        VALUES (:user_id, :category_id, :score, :correct_answers)
                    """),
                    {
                        "user_id": user_id,
                        "category_id": category_id,
                        "score": score,
                        "correct_answers": correct_answers
                    }
                )
            return True
        except Exception as e:
            logger.error(f"Error saving score for user {user_id}: {e}")
            return False

    def get_user_scores(self, user_id: int) -> List[Dict]:
        """Get user's scores across all categories"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("""
                        SELECT us.score, us.correct_answers, us.completed_at, c.name as category_name 
                        FROM user_scores us
                        JOIN categories c ON us.category_id = c.id
                        WHERE us.user_id = :user_id
                        ORDER BY us.completed_at DESC
                    """),
                    {"user_id": user_id}
                )
                return [
                    {
                        "score": row[0],
                        "correct_answers": row[1],
                        "completed_at": row[2],
                        "category_name": row[3]
                    } for row in result
                ]
        except Exception as e:
            logger.error(f"Error getting scores for user {user_id}: {e}")
            return []

    def get_category_by_slug(self, slug: str) -> Optional[Dict]:
        """Get a category by its slug"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT id, name, name_ru, slug FROM categories WHERE slug = :slug"),
                    {"slug": slug}
                ).first()
                
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "name_ru": result[2],
                        "slug": result[3]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting category by slug {slug}: {e}")
            return None 