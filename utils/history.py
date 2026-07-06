import os
import json
from datetime import datetime

HISTORY_DIR = "history"


def ensure_history():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

print("Save_histor called")
def save_history(pdf_name, summary="", question="", answer="", quiz=""):
    ensure_history()

    file_path = os.path.join(HISTORY_DIR, f"{pdf_name}.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "pdf_name": pdf_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": "",
            "chat": [],
            "quiz": ""
        }

    if summary:
        data["summary"] = summary

    if question and answer:
        data["chat"].append({
            "question": question,
            "answer": answer
        })

    if quiz:
        data["quiz"] = quiz

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_history(pdf_name):
    ensure_history()

    file_path = os.path.join(HISTORY_DIR, f"{pdf_name}.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return None

def get_history_files():
    ensure_history()

    files = []

    for file in os.listdir(HISTORY_DIR):
        if file.endswith(".json"):
            files.append(file.replace(".json", ""))

    return sorted(files)
