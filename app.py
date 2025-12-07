import streamlit as st
import random

st.set_page_config(page_title="Corporate Finance Quiz", page_icon="💼")
st.title("💼 Corporate Finance – Question-by-Question Training")

# ---------------------------------------------------------
# LOAD QUESTIONS FROM A GIVEN FILE
# ---------------------------------------------------------

def load_questions(filename: str):
    """
    Charge un fichier de questions de la forme :
    questions = [ {question, choices, answer, explanation}, ... ]
    """
    local_vars = {}
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().replace("null", "None")
        exec(content, {}, local_vars)
    return local_vars["questions"]

# ---------------------------------------------------------
# GENERIC QUIZ RUNNER (STATE PREFIXED BY TOPIC)
# ---------------------------------------------------------

def run_quiz(topic_name: str, filename: str, state_prefix: str):
    st.subheader(f"📚 {topic_name}")

    # --- Chargement des questions ---
    try:
        all_questions = load_questions(filename)
    except FileNotFoundError:
        st.error(
            f"❌ Fichier '{filename}' introuvable.\n\n"
            "Crée ce fichier dans le même dossier que app.py avec une variable `questions = [...]`."
        )
        return

    max_q = len(all_questions)
    if max_q == 0:
        st.warning("Aucune question trouvée dans ce fichier.")
        return

    # Petite fonction pour préfixer tous les noms de clé de session
    def k(name: str) -> str:
        return f"{state_prefix}_{name}"

    # ---------------------------------------------------------
    # SESSION STATE INITIALISATION (par matière)
    # ---------------------------------------------------------

    if k("seen_questions") not in st.session_state:
        st.session_state[k("seen_questions")] = set()
    if k("total_questions") not in st.session_state:
        st.session_state[k("total_questions")] = None
    if k("current_index") not in st.session_state:
        st.session_state[k("current_index")] = 0
    if k("question_order") not in st.session_state:
        st.session_state[k("question_order")] = []
    if k("answered") not in st.session_state:
        st.session_state[k("answered")] = False
    if k("score") not in st.session_state:
        st.session_state[k("score")] = 0
    if k("answers") not in st.session_state:
        st.session_state[k("answers")] = []
    if k("correct") not in st.session_state:
        st.session_state[k("correct")] = None

    # ---------------------------------------------------------
    # CHOIX DU NOMBRE DE QUESTIONS
    # ---------------------------------------------------------

    if st.session_state[k("total_questions")] is None:
        st.write("Choisis combien de questions tu veux pour cette matière :")

        remaining = max_q - len(st.session_state[k("seen_questions")])
        if remaining == 0:
            st.success("🎉 Tu as déjà vu toutes les questions de ce module ! Je réinitialise.")
            st.session_state[k("seen_questions")] = set()
            remaining = max_q

        selected_number = st.slider(
            "Nombre de questions",
            1,
            remaining,
            min(10, remaining),
            key=k("slider"),
        )

        if st.button("Start Quiz", key=k("start_quiz")):
            pool = list(set(range(max_q)) - st.session_state[k("seen_questions")])
            st.session_state[k("question_order")] = random.sample(pool, selected_number)
            st.session_state[k("total_questions")] = selected_number
            st.session_state[k("current_index")] = 0
            st.session_state[k("score")] = 0
            st.session_state[k("answers")] = []
            st.session_state[k("answered")] = False
            st.rerun()

        # On ne montre pas encore de questions tant que le quiz n’est pas lancé
        return

    # ---------------------------------------------------------
    # FIN DE QUIZ
    # ---------------------------------------------------------

    if st.session_state[k("current_index")] >= st.session_state[k("total_questions")]:
        st.success(
            "🎉 Quiz terminé ! Score final : "
            f"{st.session_state[k('score')]}/{st.session_state[k('total_questions')]}"
        )

        st.header("📘 Review of all questions")

        for i, item in enumerate(st.session_state[k("answers")], 1):
            if item["is_correct"]:
                st.markdown(f"### 🟩 Q{i}. Correct")
            else:
                st.markdown(f"### 🟥 Q{i}. Incorrect")

            st.write(f"**Question:** {item['question']}")
            st.write(f"**Your answer:** {item['your_answer']}")
            st.write(f"**Correct answer:** {item['correct_answer']}")
            st.info(f"Explanation: {item['explanation']}")

        if st.button("Restart Quiz", key=k("restart")):
            st.session_state[k("total_questions")] = None
            st.session_state[k("current_index")] = 0
            st.session_state[k("answers")] = []
            st.session_state[k("score")] = 0
            st.session_state[k("answered")] = False
            st.session_state[k("question_order")] = []
            st.session_state[k("seen_questions")] = set()
            st.rerun()

        st.stop()

    # ---------------------------------------------------------
    # BARRE DE PROGRESSION
    # ---------------------------------------------------------

    progress = st.session_state[k("current_index")] / st.session_state[k("total_questions")]
    st.progress(progress)
    st.write(
        f"Progress: **{st.session_state[k('current_index')]}/"
        f"{st.session_state[k('total_questions')]}**"
    )

    # ---------------------------------------------------------
    # QUESTION COURANTE
    # ---------------------------------------------------------

    q_index = st.session_state[k("question_order")][st.session_state[k("current_index")]]
    q = all_questions[q_index]

    st.subheader(f"Question {st.session_state[k('current_index')] + 1} :")
    st.write(q["question"])

    user_choice = st.radio(
        "Select an answer:",
        q["choices"],
        key=k(f"question_{st.session_state[k('current_index')]}"),
    )

    # ---------------------------------------------------------
    # VÉRIFICATION DE LA RÉPONSE
    # ---------------------------------------------------------

    if st.button("✔ Check Answer", key=k("check")):
        correct_answer = q["choices"][q["answer"]]

        if user_choice == correct_answer:
            st.success("Correct! 🎉")
            st.session_state[k("correct")] = True
        else:
            st.error(f"Incorrect ❌ The correct answer was: **{correct_answer}**")
            st.session_state[k("correct")] = False

        st.info(f"Explanation : {q['explanation']}")

        st.session_state[k("answers")].append({
            "question": q["question"],
            "your_answer": user_choice,
            "correct_answer": correct_answer,
            "explanation": q["explanation"],
            "is_correct": (user_choice == correct_answer),
        })

        if user_choice == correct_answer:
            st.session_state[k("score")] += 1

        st.session_state[k("answered")] = True

    # ---------------------------------------------------------
    # QUESTION SUIVANTE
    # ---------------------------------------------------------

    if st.session_state[k("answered")]:
        if st.button("👉 Next Question", key=k("next")):
            st.session_state[k("seen_questions")].add(q_index)
            st.session_state[k("current_index")] += 1
            st.session_state[k("answered")] = False
            st.rerun()

# ---------------------------------------------------------
# ONGLET PAR MATIÈRE
# ---------------------------------------------------------

tab_ma, tab_re, tab_cr = st.tabs(["M&A", "Real Estate", "Corporate Restructuring"])

with tab_ma:
    run_quiz("M&A (Mergers & Acquisitions)", "questions.txt", "ma")

with tab_re:
    run_quiz("Real Estate Finance", "questions_real_estate.txt", "re")

with tab_cr:
    run_quiz("Corporate Restructuring", "questions_corporate_restructuring.txt", "cr")
