# src/piano.py
import json
from datetime import datetime

class PianoStudi:
    def __init__(self):
        self.mesi = {
            1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
            5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
            9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre"
        }
        self.mesi_name_to_num = {v: k for k, v in self.mesi.items()}

    def carica_esami(self):
        with open('esami_ordinati.json', 'r', encoding='utf-8') as f:
            esami = json.load(f)
        
        esami_raggruppati = {}
        for esame in esami:
            nome_completo = esame["Attività Didattica"]
            nome = nome_completo.split('] ', 1)[1].strip()
            data_ora = esame["Date e ora del turno"].split('(')[0].strip()
            data = datetime.strptime(data_ora, "%d/%m/%Y - %H:%M")
            tipo = esame["Tipo"].strip() or None
            
            if nome not in esami_raggruppati:
                esami_raggruppati[nome] = []
            esami_raggruppati[nome].append((data, tipo))
        
        for nome in esami_raggruppati:
            esami_raggruppati[nome].sort(key=lambda x: x[0])
        
        return esami_raggruppati, esami

    def formatta_data(self, data):
        return f"{data.day:02}/{self.mesi[data.month]}/{data.year}"

    @staticmethod
    def allinea_testo(testo, lunghezza):
        return testo.ljust(lunghezza)[:lunghezza]

    @staticmethod
    def selezione_interattiva(opzioni, tipo):
        while True:
            try:
                scelta = input(f"\nSeleziona {tipo} (1-{len(opzioni)} o 0 per annullare): ")
                if scelta.lower() == 'exit':
                    return None
                scelta = int(scelta)
                if scelta == 0:
                    return None
                if 1 <= scelta <= len(opzioni):
                    return scelta - 1
                print("Scelta non valida!")
            except ValueError:
                print("Inserisci un numero valido!")

    def run(self):
        esami_raggruppati, esami_originali = self.carica_esami()
        piano_studi = []
            
        while True:
            nomi_esami = list(esami_raggruppati.keys())
            max_lunghezza_titolo = max(len(nome) for nome in esami_raggruppati.keys())
            
            print("\nElenco esami disponibili:")
            print(f"{'N°':<3} {'Esame':<{max_lunghezza_titolo}} {'Primo Appello':>12}")
            print("-" * (max_lunghezza_titolo + 20))
            
            for i, (nome, date_tipi) in enumerate(esami_raggruppati.items(), 1):
                mese_primo = self.mesi[date_tipi[0][0].month].capitalize()
                print(f"{i:<3} {self.allinea_testo(nome, max_lunghezza_titolo)} {mese_primo:>12}")
            
            idx_esame = self.selezione_interattiva(nomi_esami, "un esame")
            if idx_esame is None:
                risposta = input("\nVuoi uscire? (s/n): ").lower()
                if risposta == '':
                    risposta = 's'
                if risposta != 's':
                    break
                continue
            
            nome_scelto = nomi_esami[idx_esame]
            date_tipi = esami_raggruppati[nome_scelto]
            
            print(f"\nDate disponibili per {nome_scelto}:")
            for i, (data, tipo) in enumerate(date_tipi, 1):
                data_str = self.formatta_data(data)
                tipo_str = f" - {tipo}" if tipo else ""
                spazio_materia = max_lunghezza_titolo + 2
                print(f"{i:2}. {data_str} - {self.allinea_testo(nome_scelto, spazio_materia)}{tipo_str}")
            

            idx_data = self.selezione_interattiva(date_tipi, "una data")
            if idx_data is None:
                continue
            
            data_scelta, tipo_scelto = date_tipi[idx_data]
            piano_studi.append((data_scelta, nome_scelto, tipo_scelto))

        risultato = []
        max_data_len = 0
        max_materia_len = 0
        max_ultimo_len = 0
        
        for data_scelta, nome_scelto, _ in piano_studi:
            for esame in esami_originali:
                nome_completo = esame["Attività Didattica"]
                nome_esame = nome_completo.split('] ', 1)[1].strip()
                data_ora_esame_str = esame["Date e ora del turno"].split('(')[0].strip()
                data_esame = datetime.strptime(data_ora_esame_str, "%d/%m/%Y - %H:%M")
                
                if nome_esame == nome_scelto and data_esame == data_scelta:
                    ultimo_giorno_str = esame["Periodo iscrizioni (Dal - Al)"].split('-')[1].strip()
                    ultimo_giorno = datetime.strptime(ultimo_giorno_str, "%d/%m/%Y")
                    data_formattata = self.formatta_data(data_scelta)
                    ultimo_formattato = self.formatta_data(ultimo_giorno)
                    
                    max_data_len = max(max_data_len, len(data_formattata))
                    max_materia_len = max(max_materia_len, len(nome_scelto))
                    max_ultimo_len = max(max_ultimo_len, len(ultimo_formattato))
                    break
        
        for data_scelta, nome_scelto, _ in piano_studi:
            for esame in esami_originali:
                nome_completo = esame["Attività Didattica"]
                nome_esame = nome_completo.split('] ', 1)[1].strip()
                data_ora_esame_str = esame["Date e ora del turno"].split('(')[0].strip()
                data_esame = datetime.strptime(data_ora_esame_str, "%d/%m/%Y - %H:%M")
                
                if nome_esame == nome_scelto and data_esame == data_scelta:
                    ultimo_giorno_str = esame["Periodo iscrizioni (Dal - Al)"].split('-')[1].strip()
                    ultimo_giorno = datetime.strptime(ultimo_giorno_str, "%d/%m/%Y")
                    data_formattata = self.formatta_data(data_scelta)
                    ultimo_formattato = self.formatta_data(ultimo_giorno)
                    
                    data_part = data_formattata.ljust(max_data_len)
                    materia_part = nome_scelto.ljust(max_materia_len)
                    ultimo_part = ultimo_formattato.ljust(max_ultimo_len)
                    risultato.append(f"{data_part} | {materia_part} | {ultimo_part}")
                    break
        
        with open('piano_studi.json', 'w', encoding='utf-8') as f:
            json.dump(risultato, f, ensure_ascii=False, indent=2)
        
        print("\nPiano di studi salvato in piano_studi.json!")
        print("Contenuto finale:")
        print(json.dumps(risultato, indent=2))