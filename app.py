import streamlit as st
import random

st.set_page_config(page_title="Corporate Finance Quiz", page_icon="💼")

st.title("💼 Corporate Finance – Question-by-Question Training")


# ---------------------------------------------------------
# LOAD QUESTIONS.TXT
# ---------------------------------------------------------

def load_questions():
    local_vars = {}
    with open("questions.txt", "r", encoding="utf-8") as f:
        content = f.read().replace("null", "None")
        exec(content, {}, local_vars)
    return local_vars["questions"]

all_questions = load_questions()
max_q = len(all_questions)


# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------

if "seen_questions" not in st.session_state:
    st.session_state.seen_questions = set()

if "total_questions" not in st.session_state:
    st.session_state.total_questions = None

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "question_order" not in st.session_state:
    st.session_state.question_order = []

if "answered" not in st.session_state:
    st.session_state.answered = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "answers" not in st.session_state:
    st.session_state.answers = []


# ---------------------------------------------------------
# QUIZ SETUP : CHOOSE NUMBER OF QUESTIONS
# ---------------------------------------------------------

if st.session_state.total_questions is None:
    st.subheader("Choose the number of questions:")

    remaining = max_q - len(st.session_state.seen_questions)

    if remaining == 0:
        st.success("🎉 You've seen ALL the questions! Resetting.")
        st.session_state.seen_questions = set()
        remaining = max_q

    selected_number = st.slider(
        "How many questions do you want?",
        1,
        remaining,
        min(10, remaining)
    )

    if st.button("Start Quiz"):
        pool = list(set(range(max_q)) - st.session_state.seen_questions)
        st.session_state.question_order = random.sample(pool, selected_number)

        st.session_state.total_questions = selected_number
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()

    st.stop()


# ---------------------------------------------------------
# PROGRESS BAR
# ---------------------------------------------------------

progress = st.session_state.current_index / st.session_state.total_questions
st.progress(progress)

st.write(f"Progress: **{st.session_state.current_index}/{st.session_state.total_questions}**")


# ---------------------------------------------------------
# PATCH AGAINST END OF QUIZ (Prevents IndexError)
# ---------------------------------------------------------

if st.session_state.current_index >= st.session_state.total_questions:

    st.success(f"🎉 Quiz finished! Final score: {st.session_state.score}/{st.session_state.total_questions}")

    st.header("📘 Review of all questions")

    for i, item in enumerate(st.session_state.answers, 1):

        # Correct / Incorrect Header
        if item["is_correct"]:
            st.markdown(f"### 🟩 Q{i}. Correct")
        else:
            st.markdown(f"### 🟥 Q{i}. Incorrect")

        st.write(f"**Question:** {item['question']}")
        st.write(f"**Your answer:** {item['your_answer']}")
        st.write(f"**Correct answer:** {item['correct_answer']}")
        st.info(f"Explanation: {item['explanation']}")

    # Restart button
    if st.button("Restart Quiz"):
        st.session_state.total_questions = None
        st.session_state.current_index = 0
        st.session_state.answers = []
        st.session_state.score = 0
        st.rerun()

    st.stop()


# ---------------------------------------------------------
# CURRENT QUESTION
# ---------------------------------------------------------

q_index = st.session_state.question_order[st.session_state.current_index]
q = all_questions[q_index]

st.subheader(f"Question {st.session_state.current_index + 1} :")
st.write(q["question"])

user_choice = st.radio(
    "Select an answer:",
    q["choices"],
    key=f"question_{st.session_state.current_index}"
)


# ---------------------------------------------------------
# CHECK ANSWER (RE-CHECK ALLOWED)
# ---------------------------------------------------------

if st.button("✔ Check Answer"):

    correct_answer = q["choices"][q["answer"]]

    if user_choice == correct_answer:
        st.success("Correct! 🎉")
        st.session_state.correct = True
    else:
        st.error(f"Incorrect ❌ The correct answer was: **{correct_answer}**")
        st.session_state.correct = False

    st.info(f"Explanation : {q['explanation']}")

    # Record answer
    st.session_state.answers.append({
        "question": q["question"],
        "choices": q["choices"],
        "your_answer": user_choice,
        "correct_answer": correct_answer,
        "explanation": q["explanation"],
        "is_correct": (user_choice == correct_answer)
    })

    if user_choice == correct_answer:
        st.session_state.score += 1

    st.session_state.answered = True


# ---------------------------------------------------------
# NEXT QUESTION
# ---------------------------------------------------------

if st.session_state.answered:
    if st.button("👉 Next Question"):

        st.session_state.seen_questions.add(q_index)

        st.session_state.current_index += 1
        st.session_state.answered = False
        st.rerun()
