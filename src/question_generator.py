from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json
import os
import random
import re

class QuestionGenerator:
    def __init__(self, category_name="Java Basics", category_name_ru="Основы Java"):
        self.category_name = category_name
        self.category_name_ru = category_name_ru
        self.prompt_template = f"""
        You are a Java programming expert and educator. Your task is to generate questions about {category_name} ({category_name_ru}).
        Based on these existing questions:

        {{existing_questions}}

        Generate {{num_questions}} new, unique, and educational questions about {category_name}. Focus on:
        1. Core concepts and fundamentals
        2. Best practices and common patterns
        3. Common mistakes and pitfalls
        4. Practical applications
        5. Performance considerations
        
        For each question, follow this exact format:
        - All text content must be in Russian language
        - The field labels "QUESTION:", "ANSWER:", "OPTIONS:" must remain in English
        - Do not translate or modify these field labels
        - DIFFICULTY: easy, medium, hard
        - SCORE: easy=5, medium=10, hard=15
        - Do not include answer options in the question text
        - Do not include "ANSWER:" or "ОТВЕТ:" in the question text
        
        QUESTION: [your question in Russian]
        ANSWER: [correct answer in Russian]
        DIFFICULTY: [difficulty level]
        SCORE: [score for the question]
        OPTIONS:
        1. [exact same text as ANSWER above]
        2. [wrong option in Russian]
        3. [wrong option in Russian]
        4. [wrong option in Russian]
        ===

        Make sure:
        1. All content (questions, answers, and options) must be in Russian language, while keeping the field labels in English
        2. Questions are unique and not duplicates of existing ones
        3. Wrong options are plausible but clearly incorrect
        4. Each question is separated by "==="
        5. Questions should be technically accurate and reflect current Java practices
        6. Include code snippets where relevant, but keep comments and explanations in Russian
        7. Cover both theoretical concepts and practical applications
        8. The correct answer (ANSWER) must be exactly the same as the first option in OPTIONS
        9. Do not include answer options or "ANSWER:" text within the question itself
        """
        
        self.prompt = PromptTemplate(
            input_variables=["existing_questions", "num_questions"],
            template=self.prompt_template
        )
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.question_chain = self.prompt | self.llm
    
    def clean_question_text(self, text: str) -> str:
        """Clean the question text by removing answer options and answer labels"""
        # Remove everything after "ОТВЕТ:" or "ANSWER:"
        text = re.split(r'\n?(?:ОТВЕТ:|ANSWER:)', text)[0]
        
        # Remove OPTIONS section if present
        text = re.split(r'\n?OPTIONS:', text)[0]
        
        # Remove numbered options (1., 2., 3., 4.)
        text = re.sub(r'\n?\d+\. .*', '', text)
        
        # Remove any trailing whitespace or newlines
        return text.strip()

    def clean_option_text(self, text: str) -> str:
        """Clean the option text by removing answer labels and other artifacts"""
        # Remove "(Answer: ...)" patterns
        text = re.sub(r'\(Answer:.*?\)', '', text)
        
        # Remove "Answer:" text
        text = text.replace('Answer:', '').replace('ANSWER:', '')
        
        # Remove any trailing whitespace or newlines
        return text.strip()

    def generate_questions(self, existing_questions, num_questions=5):
        # Format existing questions for the prompt
        questions_text = "\n".join([
            f"- {q['question']} (Answer: {q['correct_answer']})" 
            for q in existing_questions
        ])
        
        # Generate new questions
        response = self.question_chain.invoke({
            "existing_questions": questions_text,
            "num_questions": num_questions
        })
        
        response_text = response.content
        questions = []
        question_blocks = response_text.strip().split('===')
        
        for block in question_blocks:
            if not block.strip():
                continue
                
            try:
                # Extract and clean question
                question = block[block.find('QUESTION:') + 9:block.find('ANSWER:')].strip()
                question = self.clean_question_text(question)
                
                # Extract and clean answer
                answer = block[block.find('ANSWER:') + 7:block.find('DIFFICULTY:')].strip()
                answer = self.clean_option_text(answer)
                
                # Extract difficulty
                difficulty = block[block.find('DIFFICULTY:') + 11:block.find('SCORE:')].strip()
                
                # Extract score
                score_text = block[block.find('SCORE:') + 6:block.find('OPTIONS:')].strip()
                score = int(score_text) if score_text.isdigit() else 5
                
                # Extract and clean options
                options_text = block[block.find('OPTIONS:'):].strip()
                options = []
                for line in options_text.split('\n')[1:]:
                    if line.strip() and '. ' in line:
                        option = line.split('. ', 1)[1].strip()
                        option = self.clean_option_text(option)
                        options.append(option)
                
                if len(options) == 4:
                    # Use the first option as the correct answer to ensure consistency
                    correct_answer = options[0]
                    
                    # Randomly choose position for correct answer
                    correct_position = random.randint(0, 3)
                    
                    # Rearrange options with correct answer in random position
                    shuffled_options = options[1:]
                    random.shuffle(shuffled_options)
                    
                    final_options = shuffled_options[:correct_position] + [correct_answer] + shuffled_options[correct_position:]
                    
                    questions.append({
                        'question': question,
                        'correct_answer': correct_answer,
                        'options': final_options,
                        'difficulty': difficulty.lower(),
                        'score': score
                    })
            except Exception as e:
                print(f"Error parsing question block: {e}")
                continue
        
        return questions 