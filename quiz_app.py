import streamlit as st
import json
import random
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Simulatore Esame Psichiatria", page_icon="🧠", layout="wide")

# --- LOAD DATA ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "banca_domande.json")

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def start_quiz(data):
    # Campionamento casuale di 31 domande
    selected_questions = random.sample(data, min(31, len(data)))
    
    # Prepariamo le domande con le opzioni rimescolate
    processed_questions = []
    for q in selected_questions:
        q_copy = q.copy()
        opts_items = list(q['opzioni'].items())
        random.shuffle(opts_items)
        q_copy['shuffled_options'] = dict(opts_items)
        processed_questions.append(q_copy)
        
    st.session_state.quiz_questions = processed_questions
    st.session_state.answers = {}
    st.session_state.submitted = False

# --- SESSION STATE INITIALIZATION ---
data = load_data()
if not data:
    st.error("Banca dati non trovata!")
    st.stop()

if 'quiz_questions' not in st.session_state:
    start_quiz(data)

# --- UI ---
st.title("🧠 Simulatore Esame Psichiatria")
st.sidebar.markdown(f"**Database**: {len(data)} domande")
st.markdown("Questa sessione comprende **31 domande** estratte casualmente con opzioni rimescolate.")

if st.button("🔄 Genera Nuovo Test"):
    start_quiz(data)
    st.rerun()

# --- QUIZ DISPLAY ---
# Il form deve contenere SEMPRE il submit button per funzionare
with st.form("quiz_form"):
    for idx, q in enumerate(st.session_state.quiz_questions):
        st.subheader(f"Domanda {idx + 1}")
        st.write(q['domanda'])
        
        # Recupero opzioni (se mancano per qualche motivo, fallback su quelle originali)
        options = q.get('shuffled_options', q['opzioni'])
        keys = list(options.keys())
        
        # Selezione utente
        user_choice = st.radio(
            f"Seleziona la risposta per la domanda {idx + 1}:",
            options=keys,
            format_func=lambda x: f"{options[x]}",
            key=f"radio_{q['hash']}",
            index=None if not st.session_state.submitted else keys.index(st.session_state.answers.get(q['hash'])) if st.session_state.answers.get(q['hash']) in keys else None,
            disabled=st.session_state.submitted
        )
        st.session_state.answers[q['hash']] = user_choice

        # Feedback dopo la consegna
        if st.session_state.submitted:
            correct_key = q['risposta_corretta_finale']
            is_correct = user_choice == correct_key
            if is_correct:
                st.success("**Risposta Corretta!** ✅")
            else:
                correct_text = q['opzioni'][correct_key]
                st.error(f"**Risposta Sbagliata** ❌ (Corretta: {correct_text})")
            st.info(f"**Spiegazione:** {q['spiegazione']}")
        
        st.divider()

    # Pulsante OBBLIGATORIO del form
    submitted = st.form_submit_button("Consegna il Test")

# --- LOGICA DI VALUTAZIONE ---
if submitted:
    st.session_state.submitted = True
    st.rerun()

if st.session_state.submitted:
    correct_count = sum(1 for q in st.session_state.quiz_questions if st.session_state.answers.get(q['hash']) == q['risposta_corretta_finale'])
    score = (correct_count / len(st.session_state.quiz_questions)) * 100
    
    st.header(f"📊 Risultato Finale: {correct_count} / {len(st.session_state.quiz_questions)} ({score:.1f}%)")
    if correct_count >= 18:
        st.balloons()
        st.success("Test superato! 🎉")
    else:
        st.warning("Test non superato. Continua a studiare! 💪")
