# table.py
import json
import datetime
import os

class ExamProcessor:
    def __init__(self):
        self.ESAMI_DA_FARE_FILE = "esami_da_fare.json"  # Nome file corretto
        self.RAW_TABLE_FILE = "raw_table.json"
        self.OUTPUT_FILE = "esami_ordinati.json"

    def _extract_code(self, attività: str) -> str:
        if attività.startswith("[") and "]" in attività:
            return attività.split("]")[0].lstrip("[").strip()
        return ""

    def _parse_date_turno(self, data_str: str) -> datetime.date:
        import re
        m = re.search(r"(\d{2}/\d{2}/\d{4})", data_str)
        if m:
            return datetime.datetime.strptime(m.group(1), "%d/%m/%Y").date()
        return datetime.date(1900, 1, 1)

    def run(self):
        # Carica gli esami DA FARE
        with open(self.ESAMI_DA_FARE_FILE, "r", encoding="utf-8") as f:
            esami_da_fare = json.load(f)
        codici_da_fare = set(esame["code"] for esame in esami_da_fare.values())

        # Carica la tabella completa
        with open(self.RAW_TABLE_FILE, "r", encoding="utf-8") as f:
            raw_table = json.load(f)

        # Filtra SOLO gli esami da fare
        raw_filtrato = [
            voce for voce in raw_table
            if self._extract_code(voce["Attività Didattica"]) in codici_da_fare
        ]

        # Ordina per data
        for voce in raw_filtrato:
            voce["_data"] = self._parse_date_turno(voce["Date e ora del turno"])
        raw_filtrato.sort(key=lambda v: v["_data"])
        for voce in raw_filtrato:
            del voce["_data"]

        # Salva
        with open(self.OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(raw_filtrato, f, indent=2, ensure_ascii=False)
        print(f"Creato '{self.OUTPUT_FILE}' con {len(raw_filtrato)} esami da fare ordinati.")