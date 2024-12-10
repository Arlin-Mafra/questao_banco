from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import os
from datetime import datetime

class AuthCrawler:
    def __init__(self, debug=False):
        # Setup logging
        self.logger = logging.getLogger('AuthCrawler')
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=level)
        
        # Create screenshots directory
        self.screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.logger.info("Iniciando AuthCrawler...")
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.wait = WebDriverWait(self.driver, 10)
    
    def get_screenshot_path(self, name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.screenshots_dir, f'{name}_{timestamp}.png')    
    
    def fazer_login(self, url_login, usuario, senha):
        try:
            self.logger.info(f"Acessando URL: {url_login}")
            self.driver.get(url_login)
            
            # Increase wait time and add debug logging
            self.wait = WebDriverWait(self.driver, 20)  # Increase timeout to 20 seconds
            
            self.logger.debug("Aguardando campo de login...")
            login_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "loginField"))
            )
            
            self.logger.debug("Aguardando campo de senha...")
            senha_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "passwordField"))
            )
            
            self.logger.debug("Preenchendo campos...")
            login_input.clear()
            login_input.send_keys(usuario)
            senha_input.clear()
            senha_input.send_keys(senha)
            
            # Find and click submit button (adjust selector as needed)
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            time.sleep(3)  # Wait for redirect
            
            if self.verificar_login():
                self.logger.info("Login bem sucedido!")
                return True
            else:
                self.logger.error("Falha na verificação do login")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro durante o login: {str(e)}")
            return False    
    def verificar_login(self):
        self.logger.info("Verificando status do login...")
        try:
            # Wait for page load after login attempt
            time.sleep(3)
            
            # Debug current URL
            current_url = self.driver.current_url
            self.logger.debug(f"Current URL: {current_url}")
            
            # Debug page source
            self.logger.debug("Page source after login attempt:")
            self.logger.debug(self.driver.page_source[:500])  # First 500 chars
            
            # Try multiple selectors that might indicate successful login
            selectors = [
                (By.CLASS_NAME, "perfil-usuario"),
                (By.ID, "area-aluno"),
                (By.CSS_SELECTOR, ".minha-conta"),
                # Add more selectors as needed
            ]
            
            for selector in selectors:
                try:
                    element = self.wait.until(EC.presence_of_element_located(selector))
                    self.logger.info(f"Login verificado: elemento {selector[1]} encontrado")
                    return True
                except:
                    self.logger.debug(f"Elemento {selector[1]} não encontrado")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro na verificação: {str(e)}")
            return False   
    
    def fechar(self):
        self.logger.info("Encerrando AuthCrawler...")
        if self.driver:
            self.driver.quit()


