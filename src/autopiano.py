# src/autopiano.py
import json
from datetime import datetime, timedelta
from itertools import permutations
import re

class Autopiano:
    def __init__(self):
        self.gruppi = self.carica_esami()

    @staticmethod
    def carica_esami(file_path='esami_ordinati.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            esami = json.load(f)

        gruppi = {}
        for rec in esami:
            full_name = rec['Attività Didattica']
            name = full_name.split('] ', 1)[1].strip()
            turno_str = rec['Date e ora del turno'].split('(')[0].strip()
            date = datetime.strptime(turno_str, '%d/%m/%Y - %H:%M')
            iscr_str = rec['Periodo iscrizioni (Dal - Al)'].split('-')[1].strip()
            ultimo = datetime.strptime(iscr_str, '%d/%m/%Y')

            gruppi.setdefault(name, []).append((date, ultimo))

        for name in gruppi:
            gruppi[name].sort(key=lambda x: x[0])
        return gruppi

    @staticmethod
    def formatta_data(dt):
        return dt.strftime('%d/%m/%Y')

    @staticmethod
    def parse_selezione(inp, max_idx):
        nums = re.split(r'[\s,]+', inp.strip())
        scelte = []
        for n in nums:
            if n.isdigit():
                i = int(n)
                if 1 <= i <= max_idx:
                    scelte.append(i - 1)
        return sorted(set(scelte))

    def run(self):
        nomi = list(self.gruppi.keys())

        # 1) Chiedi distanza minima
        while True:
            try:
                wk = int(input("Numero minimo di settimane tra un esame e l'altro: "))
                if wk < 0:
                    print('Inserisci un numero non negativo.')
                    continue
                break
            except ValueError:
                print('Per favore inserisci un numero valido.')
        giorni_min = wk * 7

        # 2) Mostra esami disponibili
        print("\nEsami disponibili:")
        for idx, name in enumerate(nomi, 1):
            primo = self.gruppi[name][0][0]
            print(f"{idx}. {self.formatta_data(primo)} - {name}")

        # 3) Selezione esami
        sel = input("\nSeleziona gli esami (es. 1,2,3 o 1 2 3): ")
        indici = self.parse_selezione(sel, len(nomi))
        if not indici:
            print('Nessuna selezione valida. Esco.')
            exit()
        nomi_scelti = [nomi[i] for i in indici]

        # 4) Genera combinazioni e filtra
        combos = []
        for perm in permutations(nomi_scelti):
            scelta = []
            cur_date = None
            ok = True
            for name in perm:
                found = False
                for date, ultimo in self.gruppi[name]:
                    if cur_date is None or date >= cur_date + timedelta(days=giorni_min):
                        scelta.append((name, date, ultimo))
                        cur_date = date
                        found = True
                        break
                if not found:
                    ok = False
                    break
            if ok:
                diffs = [(scelta[i+1][1] - scelta[i][1]).days for i in range(len(scelta)-1)]
                combos.append((scelta, diffs))

        if not combos:
            print(f"\nNessuna combinazione trovata con almeno {wk} settimane di distanza.")
            exit()

        # 5) Mostra combinazioni
        print("\nCombinazioni disponibili:")
        for idx, (scelta, diffs) in enumerate(combos, 1):
            print(f"\n[{idx}]")
            for j, (name, date, ultimo) in enumerate(scelta, 1):
                print(f"  {j}. {self.formatta_data(date)} - {name} (iscrizioni fino al {self.formatta_data(ultimo)})")
                if j-1 < len(diffs):
                    giorni = diffs[j-1]
                    settimane = giorni // 7
                    rest = giorni % 7
                    descr = f"{settimane} settimane e {rest} giorni" if rest else f"{settimane} settimane"
                    print(f"     distanza tra esame {j} e {j+1}: {descr} ({giorni} giorni)")

        # 6) Scelta combinazione
        while True:
            try:
                sc = int(input("\nScegli il numero della combinazione desiderata: "))
                if 1 <= sc <= len(combos):
                    scelta_finale, diffs_finale = combos[sc-1]
                    break
                print('Numero non valido.')
            except ValueError:
                print('Inserisci un numero valido.')

        # 7) Scrivi JSON
        max_data = max(len(self.formatta_data(dt)) for _, dt, _ in scelta_finale)
        max_name = max(len(name) for name, _, _ in scelta_finale)
        max_ult = max(len(self.formatta_data(ult)) for _, _, ult in scelta_finale)

        risultato = []
        for name, date, ultimo in scelta_finale:
            d = self.formatta_data(date).ljust(max_data)
            n = name.ljust(max_name)
            u = self.formatta_data(ultimo).ljust(max_ult)
            risultato.append(f"{d} | {n} | {u}")

        with open('piano_studi.json', 'w', encoding='utf-8') as f:
            json.dump(risultato, f, ensure_ascii=False, indent=2)

        print("\nPiano di studi salvato in piano_studi.json!")
        print("Contenuto finale:")
        print(json.dumps(risultato, ensure_ascii=False, indent=2))