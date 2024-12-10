from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO
import re

class PDFQuestoesCrawler:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.questions = []
        self.prova_info = {}
    
    def extract_prova_info(self, text):
        """Extrai informações básicas da prova"""
        try:
            # Procura cargo e área
            cargo_match = re.search(r"([\w-]+) - (\d{4})", text)
            area_match = re.search(r"Área: ([^\n]+)", text)
            
            if cargo_match:
                self.prova_info['cargo'] = cargo_match.group(1)
                self.prova_info['ano'] = cargo_match.group(2)
            
            if area_match:
                self.prova_info['area'] = area_match.group(1)
                
            print("Informações da prova:")
            print(self.prova_info)
            
        except Exception as e:
            print(f"Erro ao extrair informações da prova: {str(e)}")
    
    def extract_sections(self, text):
        """Extrai as seções da prova (ex: LÍNGUA PORTUGUESA)"""
        sections = {}
        current_section = None
        
        # Procura por títulos em maiúsculas
        for line in text.split('\n'):
            if line.isupper() and len(line) > 3:  # Possível título de seção
                current_section = line.strip()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line.strip())
                
        return sections
    
    def extract_questions(self, text):
        """Extrai questões do texto"""
        # Procura por padrões como "questão XX" ou numeração
        question_pattern = r'(?:questão\s+(\d+)|^(\d+)\.)'
        questions = re.split(question_pattern, text, flags=re.IGNORECASE)
        
        for q in questions:
            if q and len(q.strip()) > 10:  # Evita fragmentos muito pequenos
                print("-" * 50)
                print("Questão encontrada:")
                print(q.strip()[:200] + "...")  # Mostra início da questão
                
        return questions
    
    def read_pdf_pages(self, start_page=2):
        try:
            output = StringIO()
            with open(self.pdf_path, 'rb') as pdf_file:
                laparams = LAParams()
                extract_text_to_fp(pdf_file, output, 
                                 page_numbers=range(start_page-1, 100), 
                                 laparams=laparams)
                
            text = output.getvalue()
            
            # Remove headers e footers
            text = self.clean_text(text)
            
            # Extrai seções
            sections = self.extract_sections(text)
            
            # Para cada seção, extrai questões
            for section, content in sections.items():
                print(f"\nSeção: {section}")
                self.extract_questions('\n'.join(content))
            
            return text
            
        except Exception as e:
            print(f"Erro ao ler PDF: {str(e)}")
            return None
    
    def clean_text(self, text):
        """Remove cabeçalhos e rodapés indesejados"""
        # Remove linhas com pciconcursos
        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines 
            if not any(x in line.lower() for x in ['pcimarkpci', 'www.pciconcursos.com.br'])
        ]
        return '\n'.join(cleaned_lines)