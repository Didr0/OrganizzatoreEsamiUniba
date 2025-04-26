# lista_appelli.py
import json
import os
import platform
import datetime
import time
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from .browser import BrowserConfig

class ListaAppelli:
    def __init__(self):
        self.URL = "https://esse3.uniba.it/ListaAppelliOfferta.do"
        self.ACCOUNT_FILE = "account.json"
        self.OUTPUT_FILE = "raw_table.json"
        self.driver = None
        self.today = datetime.date.today()

    def clear_screen(self=None):
        try:
            if platform.system() == 'Windows':
                os.system('cls')
            else:
                os.system('clear')
        except:
            pass

    def _resolve_option(self, options, user_input):
        for opt in options:
            if opt.get_attribute('value') == user_input:
                return opt.get_attribute('value')
        for opt in options:
            if f"[{user_input}]" in opt.text:
                return opt.get_attribute('value')
        raise ValueError(f"Input '{user_input}' non valido")

    def _wait_for_cds(self, drv):
        return len(Select(drv.find_element(By.ID, 'selectionCds')).options) > 1

    def _prompt_user_selections(self):
        self.driver = BrowserConfig.initialize_browser(headless=True)
        self.driver.get(self.URL)
        
        start_date = self.today.strftime("%d/%m/%Y")
        end_date = (self.today + relativedelta(months=18)).strftime("%d/%m/%Y")
        self.driver.execute_script(
            f"document.getElementById('inputTextDataDa').value = '{start_date}';"
            + f"document.getElementById('inputTextDataA').value = '{end_date}';"
        )

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'selectionFacolta'))
        )

        # Department selection
        fac_select = Select(self.driver.find_element(By.ID, 'selectionFacolta'))
        print("Available Dipartimenti:")
        for opt in fac_select.options:
            print(f"{opt.get_attribute('value')}: {opt.text}")
        fac_input = input("Enter Dipartimento (value or code): ").strip()
        fac_value = self._resolve_option(fac_select.options, fac_input)
        fac_select.select_by_value(fac_value)

        # Course selection
        WebDriverWait(self.driver, 10).until(self._wait_for_cds)
        cds_select = Select(self.driver.find_element(By.ID, 'selectionCds'))
        print("Available Corsi di Studio:")
        for opt in cds_select.options:
            print(f"{opt.get_attribute('value')}: {opt.text}")
        cds_input = input("Enter Corso di Studio (value or code): ").strip()
        cds_value = self._resolve_option(cds_select.options, cds_input)

        self.driver.quit()
        
        username = input("Inserisci username ESSE3: ")
        password = input("Inserisci password ESSE3: ")
        
        return fac_value, cds_value, username, password

    def _scrape_exam_sessions(self, fac_id, cds_id):
        self.driver = BrowserConfig.initialize_browser(headless=True)
        self.driver.get(self.URL)

        # Set date range
        start_date = self.today.strftime("%d/%m/%Y")
        end_date = (self.today + relativedelta(months=18)).strftime("%d/%m/%Y")
        self.driver.execute_script(
            f"document.getElementById('inputTextDataDa').value = '{start_date}';"
            + f"document.getElementById('inputTextDataA').value = '{end_date}';"
        )

        # Select department and course
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'selectionFacolta'))
        )
        Select(self.driver.find_element(By.ID, 'selectionFacolta')).select_by_value(fac_id)
        WebDriverWait(self.driver, 10).until(self._wait_for_cds)

        cds_select = Select(self.driver.find_element(By.ID, 'selectionCds'))
        try:
            cds_select.select_by_value(cds_id)
        except NoSuchElementException:
            for opt in cds_select.options:
                if f"[{cds_id}]" in opt.text:
                    cds_select.select_by_visible_text(opt.text)
                    break

        # Execute search
        self.driver.find_element(By.ID, 'btnRicerca').click()
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'tabellaAppelli'))
        )

        time.sleep(3)
        
        rows = []
        while True:
            table = self.driver.find_element(By.ID, 'tabellaAppelli')
            # … parse rows …
            headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, 'thead th')]
            for tr in table.find_elements(By.CSS_SELECTOR, 'tbody tr'):
                cells = tr.find_elements(By.TAG_NAME, 'td')
                rows.append({headers[i]: cells[i].text.strip() for i in range(len(cells))})

            next_li = self.driver.find_element(
                By.CSS_SELECTOR,
                'li.footable-page-nav[data-page="next"]'
            )
            if 'disabled' in next_li.get_attribute('class'):
                break

            # 1) find the link
            next_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'li.footable-page-nav[data-page="next"] a')
                )
            )

            # 2) remove the pesky overlay
            self.driver.execute_script("""
                var el = document.getElementById('cm');
                if (el) { el.parentNode.removeChild(el); }
            """)

            # 3) click to the next page
            next_link.click()
            time.sleep(1)


        with open(self.OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
        self.driver.quit()
        return rows

    def run(self):
        if os.path.exists(self.ACCOUNT_FILE):
            with open(self.ACCOUNT_FILE, 'r', encoding='utf-8') as f:
                acc = json.load(f)
            fac_id, cds_id = acc['fac_id'], acc['cds_id']
        else:
            fac_id, cds_id, username, password = self._prompt_user_selections()
            self.clear_screen()
            with open(self.ACCOUNT_FILE, 'w', encoding='utf-8') as f:
                json.dump({'fac_id': fac_id, 'cds_id': cds_id, 'username': username, 'password': password}, f, ensure_ascii=False, indent=2)
        
        self._scrape_exam_sessions(fac_id, cds_id)
        print(f"Saved exam sessions to {self.OUTPUT_FILE}")