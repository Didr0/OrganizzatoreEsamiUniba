# main.py
import os
import sys
from src.lista_appelli import ListaAppelli
from src.esse3 import Esse3Scraper
from src.table import ExamProcessor
from src.piano import PianoStudi
from src.autopiano import Autopiano
from src.selezione import SelezioneEsami
from src.gcalendar import GCalendarManager 

def clean_temp_files():
    """Elimina i file temporanei generati durante l'esecuzione"""
    files_to_remove = [
        'raw_table.json',
        'esami_da_fare.json'
    ]
    
    for file in files_to_remove:
        try:
            os.remove(file)
            print(f"File temporaneo cancellato: {file}")
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Errore cancellando {file}: {str(e)}")

def main():
    while True:
        print("\n--- Menu ---")
        print("1. Recupera appelli")
        print("2. Scegli appelli")
        print("3. Aggiungi esami al calendario")
        print("4. Esci")
        scelta = input("Seleziona un'opzione: ").strip()

        if scelta == '1':
            lista_appelli = ListaAppelli()
            lista_appelli.run()
            
            esse3_scraper = Esse3Scraper()
            esse3_scraper.run()
            
            processor = ExamProcessor()
            processor.run()
            clean_temp_files()
            print("\nDati aggiornati correttamente.")

        elif scelta == '2':
            print("\n--- Scelta appelli ---")
            print("1. Automatica")
            print("2. Manuale")
            modalita = input("Seleziona la modalità (1/2): ").strip()
            if modalita == '1':
                autopiano = Autopiano()
                autopiano.run()
                print("\nPiano di studi completato.")
            elif modalita == '2':
                piano_studi = PianoStudi()
                piano_studi.run()
                print("\nPiano di studi completato.")
            else:
                print("Opzione non valida. Riprova.")
                continue

        elif scelta == '3':
            selezione = SelezioneEsami()
            selezione.run()
            calendar_manager = GCalendarManager()
            calendar_manager.run()
        
        elif scelta == '4':
            print("Arrivederci!")
            sys.exit()
        
        else:
            print("Opzione non valida. Riprova.")

if __name__ == "__main__":
    main()