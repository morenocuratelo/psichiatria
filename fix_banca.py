import json
import os

file_path = r"E:\Etc\PythonSandbox\psichiatria26\banca_domande.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

new_data = []

for q in data:
    h = q["hash"]
    domanda = q["domanda"]

    # 1. ELIMINAZIONE domande ricordate male (testo monco con puntini sospensivi nelle risposte)
    if "ostacolo che le impedisce" in domanda or "importanti obiettivi vitali" in domanda:
        continue # Salta questa domanda
    
    # 2. FIX q_1787737ec3 e q_3381a18413: Depersonalizzazione fusa
    if "depersonalizzazione e derealizzazione" in domanda.lower():
        q["domanda"] = "Quale delle seguenti affermazioni sul disturbo di depersonalizzazione e derealizzazione è vera?"
        q["opzioni"] = {
            "a": "I sintomi possono presentarsi durante un attacco di panico",
            "b": "L'esame di realtà è tipicamente compromesso (delirio)",
            "c": "I sintomi si manifestano esclusivamente durante l'uso di sostanze",
            "d": "È un disturbo tipico della terza età"
        }
        q["risposta_corretta_finale"] = "a"
        q["spiegazione"] = "La depersonalizzazione e la derealizzazione possono essere sintomi associati a un attacco di panico o a un episodio depressivo, pur costituendo un disturbo autonomo se persistenti."

    # 3. FIX q_11: Modelli psicodinamici DCA (Nessuna -> Tutte)
    if "modelli psicodinamici" in domanda.lower() and "dca" in domanda.lower():
        # Sostituisco 'Nessuna delle precedenti' con 'Tutte le precedenti' e rendo corretta
        for k, v in q["opzioni"].items():
            if "nessuna" in v.lower():
                q["opzioni"][k] = "Tutte le precedenti"
                q["risposta_corretta_finale"] = k
        q["spiegazione"] = "L'approccio psicodinamico ai DCA integra la lettura dei sintomi, il vissuto soggettivo della paziente e le dinamiche relazionali/familiari sottostanti."

    # 4. FIX q_184: Fattore prognostico Schizofrenia (Spiegazione incoerente)
    if "fattore prognostico" in domanda.lower() and "schizofrenia" in domanda.lower():
        q["domanda"] = "Quale dei seguenti NON è considerato un fattore prognostico favorevole della schizofrenia?"
        q["risposta_corretta_finale"] = "d" # Età d'esordio precoce
        q["spiegazione"] = "Un esordio precoce (adolescenziale) correla solitamente con una prognosi peggiore, a differenza di un esordio acuto, del sesso femminile o della prevalenza di sintomi positivi."

    # 5. Pulizia generale Schizofrenia (Spiegazioni boilerplate residue)
    if "schizofrenia" in domanda.lower() and "segni continuativi... 6 mesi" in q["spiegazione"]:
        # Se la domanda non riguarda i criteri temporali, cambio la spiegazione
        if "prognostic" not in domanda.lower() and "durata" not in domanda.lower():
            q["spiegazione"] = "La schizofrenia è un disturbo del neurosviluppo con esordio tipico in giovane età e decorso spesso cronico-remittente."

    new_data.append(q)

# Salvataggio
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=2, ensure_ascii=False)

print(f"Bonifica chirurgica completata. Domande rimanenti: {len(new_data)}")
