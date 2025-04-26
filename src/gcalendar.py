# src/gcalendar.py
import json
import os
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from src.browser import BrowserConfig

class GCalendarManager:
    def __init__(self):
        self.driver = None
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def crea_evento(self, titolo, data, reminders):
        """Crea un evento su Google Calendar con gestione avanzata dei promemoria."""
        try:
            start_time = data
            end_time = start_time + timedelta(hours=1)
            
            base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
            params = {
                'text': titolo,
                'dates': f"{start_time.strftime('%Y%m%dT%H%M%S')}/{end_time.strftime('%Y%m%dT%H%M%S')}"
            }
            self.driver.get(f"{base_url}&{urllib.parse.urlencode(params)}")

            # Attendi caricamento pagina
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
            )

            # Rimuovi notifiche predefinite
            while True:
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Rimuovi notifica']"))
                    ).click()
                    time.sleep(1)
                except:
                    break

            # Aggiungi nuovi promemoria
            for giorni in reminders:
                self._aggiungi_promemoria(giorni)

            # Imposta colore evento
            self._imposta_colore()

            # Salva evento
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Salva']"))
            ).click()
            time.sleep(2)
            
        except Exception as e:
            print(f"Errore durante la creazione dell'evento '{titolo}': {str(e)}")

    def _aggiungi_promemoria(self, giorni):
        """Funzione helper per aggiungere un singolo promemoria"""
        try:
            # Aggiungi nuova notifica
            notifiche_pre = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'COCaHe')]/li")
            n_pre = len(notifiche_pre)
            
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Aggiungi notifica']"))
            ).click()
            
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//ul[contains(@class, 'COCaHe')]/li")) == n_pre + 1
            )
            time.sleep(0.5)

            # Configura nuova notifica
            last_li = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'COCaHe')]/li")[-1]
            
            # Seleziona tipo notifica (Email)
            combobox = last_li.find_element(By.XPATH, ".//div[@role='combobox' and @aria-label='Metodo di notifica']")
            combobox.click()
            WebDriverWait(last_li, 5).until(
                EC.visibility_of_element_located((By.XPATH, ".//li[@role='option']//span[contains(., 'Email')]"))
            ).click()
            time.sleep(0.3)

            # Inserisci giorni
            input_field = last_li.find_element(By.XPATH, ".//input[@type='number']")
            input_field.clear()
            input_field.send_keys(str(giorni))
            
            # Seleziona unità di tempo
            dropdown = last_li.find_element(By.XPATH, ".//div[@role='combobox' and @aria-label='Selezione unità di tempo']")
            dropdown.click()
            WebDriverWait(last_li, 5).until(
                EC.visibility_of_element_located((By.XPATH, ".//li[@role='option' and @data-value='86400']"))
            ).click()
            time.sleep(0.3)

        except Exception as e:
            print(f"Errore nell'aggiunta del promemoria a {giorni} giorni: {str(e)}")

    def _imposta_colore(self):
        """Imposta il colore dell'evento su giallo"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label[contains(., 'Colore calendario')]]"))
            ).click()
            
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-color='#F6BF26']"))
            ).click()
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Errore nell'impostazione del colore: {str(e)}")

    def run(self):
        """Esegue il processo completo di creazione eventi"""
        try:
            # Carica esami selezionati
            with open(os.path.join(self.root_dir, 'esami_selezionati.json'), 'r', encoding='utf-8') as f:
                esami = json.load(f)
        except FileNotFoundError:
            print("Errore: File esami_selezionati.json non trovato. Eseguire prima la selezione degli esami.")
            return

        # Prepara lista eventi
        eventi = []
        for esame in esami:
            materia = esame["Attività Didattica"].split("] ")[-1].strip()
            
            # Data esame
            data_ora = esame["Date e ora del turno"].split(" - ")
            data_appello = datetime.strptime(f"{data_ora[0].strip()} {data_ora[1].strip()}", "%d/%m/%Y %H:%M")
            
            # Data scadenza iscrizione
            scadenza = esame["Periodo iscrizioni (Dal - Al)"].split("- ")[-1].strip()
            data_iscrizione = datetime.strptime(scadenza, "%d/%m/%Y").replace(hour=12, minute=0)
            
            eventi.extend([
                {'titolo': materia, 'data': data_appello, 'reminders': [7, 14]},
                {'titolo': f"Iscr. {materia}", 'data': data_iscrizione, 'reminders': [1]}
            ])

        # Inizializza browser
        self.driver = BrowserConfig.initialize_browser(headless=False)
        
        try:
            self.driver.get("https://calendar.google.com")
            input("Effettua il login manuale su Google Calendar e premi INVIO per continuare...")
            
            for evento in eventi:
                print(f"Creazione evento: {evento['titolo']} - {evento['data']}")
                self.crea_evento(
                    evento['titolo'],
                    evento['data'],
                    evento['reminders']
                )
                time.sleep(2)
                
            print("\nProcesso completato! Eventi aggiunti a Google Calendar.")
            
        except Exception as e:
            print(f"Errore critico durante l'esecuzione: {str(e)}")
        finally:
            self.driver.quit()