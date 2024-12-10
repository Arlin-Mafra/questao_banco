import os
import json
from questoes.models import Questao, QuestaoMultiplaEscolha, QuestaoCertoErrado

class QuestoesCrawler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.questions = []
    
    def read_questions(self):
        """Read questions from file based on extension"""
        _, ext = os.path.splitext(self.file_path)
        
        if ext.lower() == '.json':
            return self.read_json()
        elif ext.lower() == '.txt':
            return self.read_txt()
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def read_json(self):
        """Read questions from JSON file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.questions = json.load(file)
                return len(self.questions)
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}")
            return 0
    
    def read_txt(self):
        """Read questions from structured text file"""
        questions = []
        current_question = {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("QUESTAO:"):
                        if current_question:
                            questions.append(current_question)
                        current_question = {"enunciado": line[8:].strip()}
                    elif line.startswith("TIPO:"):
                        current_question["tipo"] = line[5:].strip()
                    # Add more parsing logic as needed
                
                if current_question:
                    questions.append(current_question)
                
                self.questions = questions
                return len(questions)
        except Exception as e:
            print(f"Error reading text file: {str(e)}")
            return 0
