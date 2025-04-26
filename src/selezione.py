import json
import os

class SelezioneEsami:
    mesi = {
        'gennaio': '01',
        'febbraio': '02',
        'marzo': '03',
        'aprile': '04',
        'maggio': '05',
        'giugno': '06',
        'luglio': '07',
        'agosto': '08',
        'settembre': '09',
        'ottobre': '10',
        'novembre': '11',
        'dicembre': '12'
    }

    @classmethod
    def converti_data(cls, data_str):
        parti = data_str.strip().split('/')
        giorno = parti[0].zfill(2)
        month_part = parti[1].strip().lower()
        if month_part.isdigit():
            mese = month_part.zfill(2)
        else:
            mese = cls.mesi[month_part]
        anno = parti[2].strip()
        return f"{giorno}/{mese}/{anno}"

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)

        # Carica piano_studi.json
        piano_studi = []
        try:
            with open(os.path.join(root_dir, 'piano_studi.json'), 'r', encoding='utf-8') as f:
                for riga in json.load(f):
                    parti = riga.strip().split('|')
                    if len(parti) >= 3:
                        data_appello = self.converti_data(parti[0].strip())
                        nome_esame = parti[1].strip()
                        piano_studi.append((nome_esame, data_appello))
        except FileNotFoundError:
            print("Errore: piano_studi.json non trovato.")
            return

        # Carica esami_ordinati.json
        try:
            with open(os.path.join(root_dir, 'esami_ordinati.json'), 'r', encoding='utf-8') as f:
                esami = json.load(f)
        except FileNotFoundError:
            print("Errore: esami_ordinati.json non trovato.")
            return

        # Trova corrispondenze
        esami_selezionati = []
        for esame in esami:
            nome_completo = esame['Attività Didattica']
            nome_pulito = nome_completo.split('] ')[-1].strip()
            data_esame = esame['Date e ora del turno'].split(' - ')[0].strip()
            
            for nome_piano, data_piano in piano_studi:
                if nome_pulito == nome_piano and data_esame == data_piano:
                    esami_selezionati.append(esame)
                    break

        # Salva risultati
        with open(os.path.join(root_dir, 'esami_selezionati.json'), 'w', encoding='utf-8') as f:
            json.dump(esami_selezionati, f, ensure_ascii=False, indent=2)
        
        print(f"Trovati {len(esami_selezionati)} appelli corrispondenti!")