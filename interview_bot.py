import streamlit as st
import openai
import os

# Set your OpenAI API key here
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state
if "job_role" not in st.session_state:
    st.session_state.job_role = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""
if "question_number" not in st.session_state:
    st.session_state.question_number = 1


# Function to generate a new question
def generate_question(job_role, chat_history):
    system_prompt = "You are a professional AI interview coach helping users prepare for real job interviews."

    user_prompt = f"""
The user is preparing for a {job_role} interview.

Your task is to act as the interviewer. Ask one relevant interview question at a time, specific to the role of {job_role}.
Do not answer for the user. Wait for the user’s answer.

Here is the current interview so far:
{chat_history}

Ask the next question.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


# Function to evaluate user response
def evaluate_answer(job_role, question, answer):
    prompt = f"""
You are an expert interview coach.

The user is preparing for a {job_role} interview.

Question: {question}
User Answer: {answer}

Please provide concise, constructive feedback on the answer. Mention strengths and offer at least one improvement tip.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You provide expert interview feedback."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


# Streamlit App UI
st.title("AI Interview Coach")
st.write("Practice answering interview questions tailored to your target job role.")

# Job role input
if st.session_state.job_role == "":
    st.session_state.job_role = st.text_input("What role are you preparing for?")
    if st.session_state.job_role:
        st.session_state.chat_history = ""
        st.session_state.question_number = 1
        st.experimental_rerun()
else:
    st.subheader(f"Interview Role: {st.session_state.job_role}")

    if st.button("🔄 Change Role"):
        st.session_state.job_role = ""
        st.session_state.chat_history = ""
        st.experimental_rerun()

    # Ask question
    if "current_question" not in st.session_state:
        st.session_state.current_question = generate_question(
            st.session_state.job_role,
            st.session_state.chat_history
        )

    st.markdown(f"**Q{st.session_state.question_number}:** {st.session_state.current_question}")
    user_answer = st.text_area("Your Answer", key="answer_box")

    if st.button("Submit Answer"):
        st.session_state.chat_history += f"\nQ{st.session_state.question_number}: {st.session_state.current_question}\nA{st.session_state.question_number}: {user_answer}\n"
        feedback = evaluate_answer(
            st.session_state.job_role,
            st.session_state.current_question,
            user_answer
        )
        st.markdown("### 💬 Feedback")
        st.success(feedback)

        # Prepare for next question
        st.session_state.question_number += 1
        st.session_state.current_question = generate_question(
            st.session_state.job_role,
            st.session_state.chat_history
        )
        st.experimental_rerun()
