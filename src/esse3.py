# esse3.py
import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .browser import BrowserConfig

class Esse3Scraper:
    def __init__(self):
        self.CREDENTIALS_FILE = 'account.json'
        self.EXAMS_FILE = 'esami_da_fare.json'
        self.LOGIN_URL = 'https://esse3.uniba.it/auth/Logon.do'
        self.driver = None

    def _handle_career_selection(self):
        try:
            # Controlla se è presente la tabella di selezione carriera
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'gu_table_sceltacarriera'))
            )
            time.sleep(1.5)

            rows = self.driver.find_elements(By.CSS_SELECTOR, '#gu_table_sceltacarriera tbody tr')
            if len(rows) == 1:
                # Seleziona automaticamente l'unica opzione
                rows[0].find_element(By.CSS_SELECTOR, 'a.toolbar-button-blu').click()
                return

            # Mostra opzioni all'utente
            print("\n--- Carriere disponibili ---")
            careers = []
            for i, row in enumerate(rows, 1):
                cells = row.find_elements(By.TAG_NAME, 'td')
                career_type = cells[1].text
                course = cells[2].text
                status = cells[3].text
                careers.append({
                    'id': cells[4].find_element(By.TAG_NAME, 'a').get_attribute('href').split('stu_id=')[1],
                    'text': f"{course} ({career_type}) - Stato: {status}"
                })
                print(f"{i}. {careers[-1]['text']}")

            # Input utente
            choice = int(input("Seleziona il numero della carriera: ")) - 1
            while choice < 0 or choice >= len(rows):
                choice = int(input("Scelta non valida. Riprova: ")) - 1

            # Seleziona la carriera
            rows[choice].find_element(By.CSS_SELECTOR, 'a.toolbar-button-blu').click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'hamburger'))
            )
            
        except TimeoutException:
            # Nessuna selezione carriera necessaria
            pass

    def _load_credentials(self):
        if os.path.exists(self.CREDENTIALS_FILE):
            with open(self.CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['username'], data['password']

    def _save_pending_exams(self, pending):
        exams_dict = {}
        if os.path.exists(self.EXAMS_FILE):
            try:
                with open(self.EXAMS_FILE, 'r', encoding='utf-8') as f:
                    exams_dict = json.load(f)
            except json.JSONDecodeError:
                exams_dict = {}
        for exam in pending:
            exams_dict[exam['code']] = exam
        with open(self.EXAMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(exams_dict, f, ensure_ascii=False, indent=2)
        print(f"Salvati {len(pending)} esami da fare nel file '{self.EXAMS_FILE}'")

    def _extract_exams(self):
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.element_to_be_clickable((By.ID, 'hamburger'))).click()
        wait.until(EC.element_to_be_clickable((By.ID, 'menu_link-navbox_studenti_Carriera'))).click()
        wait.until(EC.element_to_be_clickable((By.ID, 'menu_link-navbox_studenti_auth/studente/Libretto/LibrettoHome'))).click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody.table-1-body tr')))
        
        rows = self.driver.find_elements(By.CSS_SELECTOR, 'tbody.table-1-body tr')

        pending_exams = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            try:
                status_img = cells[3].find_element(By.TAG_NAME, 'img')
                status = status_img.get_attribute('title') or status_img.get_attribute('alt')
            except Exception:
                status = ''
                
            if 'Superata' in status:
                continue

            code_name = cells[0].text.strip()
            code, name = (code_name.split(' - ', 1) if ' - ' in code_name else (code_name, ''))

            pending_exams.append({
                'code': code,
                'name': name,
                'grade': '',
                'date': ''
            })
        return pending_exams

    def run(self):
        username, password = self._load_credentials()
        self.driver = BrowserConfig.initialize_browser(headless=True)
        try:
            self.driver.get(self.LOGIN_URL)
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.element_to_be_clickable((By.ID, 'username'))).send_keys(username)
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.NAME, '_eventId_proceed').click()

            # Gestione selezione carriera
            self._handle_career_selection()
            
            pending_exams = self._extract_exams()
            if pending_exams:
                self._save_pending_exams(pending_exams)
            else:
                print('Nessun esame da fare trovato.')
        finally:
            time.sleep(2)
            self.driver.quit()