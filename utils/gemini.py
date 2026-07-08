import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Pehle .env se key lo
API_KEY = os.getenv("GEMINI_API_KEY")

# Agar .env me nahi mili to Streamlit Secrets se lo
if not API_KEY:
    API_KEY = st.secrets["GEMINI_API_KEY"]

# Client banao
client = genai.Client(api_key=API_KEY)

def ask_gemini(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text