import streamlit as st
import os
import json

# नियम: Page Configuration हमेशा सबसे पहले होना चाहिए
st.set_page_config(
    page_title="EduSathi AI",
    page_icon="🎓",
    layout="wide"
)

from utils.pdf_export import create_pdf
from utils.pdf_reader import read_pdf
from utils.gemini import ask_gemini
from utils.history import save_history, load_history, get_history_files

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = ""

if "notes" not in st.session_state:
    st.session_state.notes = ""

# Load Custom CSS securely
if os.path.exists("assets/style.css"):
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Sidebar Navigation
page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "🤖 AI Tutor",
        "📄 PDF Summary",
        "📝 Quiz Generator",
        "📂 History",
        "📅 Study Planner"
    ]
)

# --- 1. HOME PAGE ---
if page == "🏠 Home":
    st.title("🎓 EduSathi AI")
    st.markdown(
        """
        ### Your Personal Rural Education Assistant
        Learn smarter with AI.
        
        ✅ AI Tutor
        ✅ Quiz Generator
        ✅ Study Planner
        ✅ Hindi + English Support
        """
    )
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🤖 AI Tutor\n\nAsk any question and get instant explanations.")
    with col2:
        st.info("📝 Quiz Generator\n\nGenerate quizzes on any topic.")

    col3, col4 = st.columns(2)
    with col3:
        st.info("📅 Study Planner\n\nCreate a personalized study plan.")
    with col4:
        st.info("🌐 Multi-language\n\nLearn in Hindi or English.")

# --- 2. PDF SUMMARY PAGE ---
elif page == "📄 PDF Summary":
    st.title("📄 AI PDF Summary")
    
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_file is not None:
        st.success("PDF uploaded successfully!")
        pdf_text = read_pdf(uploaded_file)
        pdf_name = uploaded_file.name.replace(".pdf", "")
        
        # FIXED: Added 'f' before string for variable parsing
        st.info(f"""
        📄 **File Name:** {uploaded_file.name}
        📦 **Size:** {round(uploaded_file.size / (1024*1024), 2)} MB
        """)
        
        language = st.selectbox("🌍 Output Language", ["English", "Hindi", "Hinglish"])
        
        # --- Section A: Generate Summary ---
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                prompt = f"""
                Respond only in {language}.
                Summarize the following PDF in simple language.
                Keep the summary concise and easy to understand.

                {pdf_text[:15000]}
                """
                st.session_state.summary = ask_gemini(prompt)
                save_history(pdf_name, summary=st.session_state.summary)
                
        if st.session_state.summary:
            st.subheader("Summary")
            st.write(st.session_state.summary)
            
        st.markdown("---")

        # --- Section B: Ask Questions ---
        question = st.text_input("Ask anything about this PDF")
        if st.button("Ask PDF"):
            if question.strip():
                prompt = f"""
                Respond only in {language}.
                Answer only from this PDF.

                PDF:
                {pdf_text[:15000]}

                Question:
                {question}
                """
                st.session_state.answer = ask_gemini(prompt)
                save_history(pdf_name, question=question, answer=st.session_state.answer)
            else:
                st.warning("Please enter a question.")

        if st.session_state.answer:
            st.subheader("Answer")
            st.write(st.session_state.answer)

        st.markdown("---")
        
        # --- Section C: Quiz Generator from PDF ---
        difficulty = st.selectbox("🎯 Quiz Difficulty", ["Easy", "Medium", "Hard"])
        
        if st.button("Generate Quiz from PDF"):
            with st.spinner("Creating quiz..."):
                quiz_prompt = f"""
                Respond only in {language}.
                Generate a {difficulty} level quiz.
                Based on this PDF, generate 10 multiple choice questions.

                Format:
                Q1.
                A)
                B)
                C)
                D)

                Mention the correct answer after each question.

                PDF:
                {pdf_text[:15000]}
                """
                st.session_state.quiz = ask_gemini(quiz_prompt)
                save_history(pdf_name, quiz=st.session_state.quiz)
                
        if st.session_state.quiz:
            st.subheader("Quiz")
            st.write(st.session_state.quiz)

        st.markdown("---")

        # --- Section D: Smart Notes ---
        if st.button("📝 Generate Smart Notes"):
            with st.spinner("Generating Notes..."):
                notes_prompt = f"""
                Respond only in {language}.
                Create smart study notes from this PDF.

                Include:
                - Key Points
                - Important Definitions
                - Important Formulas (if any)
                - Important Facts
                - Exam Tips

                Use simple language.

                PDF:
                {pdf_text[:15000]}
                """
                # FIXED: Added the missing ask_gemini call
                st.session_state.notes = ask_gemini(notes_prompt)

        if st.session_state.notes:
            st.subheader("📝 Smart Notes")
            st.write(st.session_state.notes)

# --- 3. AI TUTOR PAGE ---
elif page == "🤖 AI Tutor":
    st.title("🤖 EduSathi AI Tutor")

    topic = st.text_area(
        "Ask your question",
        placeholder="Example: Explain Newton's Laws in simple Hindi."
    )
    
    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    if st.button("Generate Answer"):
        if topic.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    st.session_state.messages.append({"role": "user", "content": topic})
                    answer = ask_gemini(topic)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Force rerun to show the latest chat message properly
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 4. HISTORY PAGE ---
elif page == "📂 History":
    st.title("📂 History")
    files = get_history_files()

    if not files:
        st.info("No history found.")
    else:
        selected = st.selectbox("Select a PDF", files)
        data = load_history(selected)

        if data:
            st.subheader("📄 Summary")
            st.write(data.get("summary", "No summary available."))
            st.markdown("---")

            st.subheader("❓ Questions & Answers")
            chat = data.get("chat", [])
            if chat:
                for item in chat:
                    st.markdown(f"**Q:** {item['question']}")
                    st.write(item["answer"])
                    st.markdown("---")
            else:
                st.info("No questions asked.")

            st.subheader("📝 Quiz")
            st.write(data.get("quiz", "No quiz generated for this file."))

# --- 5. QUIZ GENERATOR PAGE ---
elif page == "📝 Quiz Generator":
    st.title("📝 Quiz Generator")
    st.info("Coming Soon...")

# --- 6. STUDY PLANNER PAGE ---
elif page == "📅 Study Planner":
    st.title("📅 AI Study Planner")
    exam = st.text_input("Exam Name", placeholder="UP SI / Class 10 / JEE")
    subject = st.text_input("Subject", placeholder="Maths")
    days = st.number_input("Days Left", min_value=1, max_value=365, value=30)
    hours = st.number_input("Study Hours per Day", min_value=1, max_value=16, value=4)

    if st.button("Generate Study Plan"):
        with st.spinner("Creating your study plan..."):
            prompt = f"""
            You are an expert study planner.
            Create a day-wise study plan.
            Exam: {exam}
            Subject: {subject}
            Days Left: {days}
            Study Hours Per Day: {hours}

            Requirements:
            - Make a daily timetable.
            - Divide topics evenly.
            - Include revision days.
            - Include practice questions.
            - Keep the language simple.
            - Format it nicely.
            """
            plan = ask_gemini(prompt)
            st.subheader("📅 Your Personalized Study Plan")
            st.write(plan)
