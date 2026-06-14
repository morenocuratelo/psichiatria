import streamlit as st
import json
import random
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Simulatore Esame Psichiatria", page_icon="🧠", layout="wide")

# --- LOAD DATA ---
# Get the absolute path of the directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "banca_domande.json")

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def start_quiz(data):
    st.session_state.quiz_questions = random.sample(data, min(31, len(data)))
    st.session_state.answers = {}
    st.session_state.submitted = False

# --- SESSION STATE ---
if 'quiz_questions' not in st.session_state:
    data = load_data()
    if data:
        start_quiz(data)
    else:
        st.error("Banca dati non trovata! Assicurati che banca_domande.json sia presente.")
        st.stop()

# --- UI ---
st.title("🧠 Simulatore Esame Psichiatria")
st.markdown("Questa sessione comprende **31 domande** estratte casualmente dalla banca dati validata.")

if st.sidebar.button("Ricomincia con nuove domande"):
    data = load_data()
    start_quiz(data)
    st.rerun()

# --- QUIZ DISPLAY ---
with st.form("quiz_form"):
    for idx, q in enumerate(st.session_state.quiz_questions):
        st.subheader(f"Domanda {idx + 1}")
        st.write(q['domanda'])
        
        # Options mapping
        options = q['opzioni']
        sorted_keys = sorted(options.keys())
        
        # User selection
        user_ans = st.radio(
            f"Seleziona la risposta per la domanda {idx + 1}:",
            options=sorted_keys,
            format_func=lambda x: f"{x.upper()}: {options[x]}",
            key=f"radio_{q['hash']}",
            index=None if not st.session_state.submitted else sorted_keys.index(st.session_state.answers.get(q['hash'])) if st.session_state.answers.get(q['hash']) in sorted_keys else None,
            disabled=st.session_state.submitted
        )
        st.session_state.answers[q['hash']] = user_ans

        # --- IMMEDIATE FEEDBACK ---
        if st.session_state.submitted:
            correct_ans = q['risposta_corretta_finale']
            is_correct = user_ans == correct_ans
            if is_correct:
                st.success(f"**Risposta Corretta!** ✅")
            else:
                st.error(f"**Risposta Sbagliata** ❌ (Corretta: {correct_ans.upper()}: {options.get(correct_ans, '')})")
            st.info(f"**Spiegazione:** {q['spiegazione']}")
        
        st.divider()

    submitted = st.form_submit_button("Consegna il Test", disabled=st.session_state.submitted)

# --- EVALUATION LOGIC ---
if submitted:
    st.session_state.submitted = True
    st.rerun()

if st.session_state.submitted:
    correct_count = sum(1 for q in st.session_state.quiz_questions if st.session_state.answers.get(q['hash']) == q['risposta_corretta_finale'])
    score_percentage = (correct_count / len(st.session_state.quiz_questions)) * 100
    st.header(f"📊 Risultato Finale: {correct_count} / {len(st.session_state.quiz_questions)} ({score_percentage:.1f}%)")
    if correct_count >= 18:
        st.balloons()
        st.success("Test superato! 🎉")
    else:
        st.warning("Test non superato. Continua a studiare! 💪")
