import logging
from database import Database
from question_generator import QuestionGenerator
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_questions_for_category(db, category_id, category_name, category_name_ru, num_questions=30):
    logger.info(f"Starting question generation for {category_name} (ID: {category_id})")
    
    generator = QuestionGenerator(category_name, category_name_ru)
    existing_questions = db.get_existing_questions(category_id)
    logger.info(f"Found {len(existing_questions)} existing questions for {category_name}")
    
    total_questions = 0
    batch_size = 15
    
    while total_questions < num_questions:
        try:
            current_batch = min(batch_size, num_questions - total_questions)
            logger.info(f"Generating batch of {current_batch} questions ({total_questions + 1}-{total_questions + current_batch})")
            
            new_questions = generator.generate_questions(existing_questions, current_batch)
            
            # Handle single AIMessage response
            if hasattr(new_questions, 'content'):
                new_questions = [new_questions]
            
            # Convert AIMessage to dictionary if needed
            processed_questions = []
            for question in new_questions:
                try:
                    # Handle both AIMessage objects and dictionary responses
                    if hasattr(question, 'content'):
                        # Assuming the content is a string containing the question
                        question_data = {'question': question.content.strip()}
                    else:
                        question_data = question
                    
                    success = db.insert_question(question_data, category_id)
                    if success:
                        total_questions += 1
                        logger.info(f"✓ Added ({total_questions}/{num_questions}): {question_data['question']}")
                        processed_questions.append(question_data)
                    else:
                        logger.error(f"✗ Failed to add: {question_data['question']}")
                except AttributeError as e:
                    logger.error(f"Error processing question object: {str(e)}")
                    logger.debug(f"Question object type: {type(question)}")
                    continue
            
            existing_questions.extend(processed_questions)
            
            # Only add delay if no questions were processed in this batch
            if not processed_questions:
                logger.info("No questions processed in this batch, waiting 5 seconds before retry...")
                time.sleep(5)
                
        except Exception as e:
            logger.error(f"Error in batch generation: {str(e)}")
            logger.debug("Full error:", exc_info=True)
            time.sleep(5)  # Only wait on error
            continue
    
    logger.info(f"Successfully added {total_questions} new questions for {category_name}!")
    return total_questions

def main():
    try:
        db = Database()
        
        # Get all categories from database
        categories = db.get_categories()
        logger.info(f"Found {len(categories)} categories in database")
        
        total_questions = 0
        for category in categories:
            questions_added = generate_questions_for_category(
                db=db,
                category_id=category['id'],
                category_name=category['name'],
                category_name_ru=category['name_ru']
            )
            total_questions += questions_added
            logger.info(f"Completed processing for {category['name']}")
            logger.info("-" * 50)
        
        logger.info(f"Operation completed: Added {total_questions} questions across all categories!")
            
    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 