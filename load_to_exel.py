import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


services_list = [
    "Комп'ютерна діагностика",
    "Заміна оливи ДВЗ + масляний фільтр",
    "Комплексна діагностика",
    "Ендоскопія",
    "Заміна повітряного фільтра ДВЗ",
    "Заміна фільтра салону в салонному відділенні",
    "Заміна сайлентблоку",
    "Зняття / встановлення важеля",
    "Заміна еластичної муфти карданного валу",
    "Слюсарні роботи",
    "Комплексна діагностика підвіски",
    "Зняття / встановлення важеля прд.",
    "Заміна амортизатора переднього",
    "Заміна оливи АКПП",
    "Мийка / чистка деталі",
    "Зняття / встановлення повітряного патрубка",
    "Заміна охолоджувальної рідини",
    "Заміна гальмівної рідини з прокачкою",
    "Заміна оливи в зд. редукторі"
]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class CallAnalysis(BaseModel):
    job_type: str = Field(description="Вибраний тип робіт зі списку")
    manager_rating: int = Field(description="Оцінка від 1 до 5")
    is_ok: bool = Field(description="true якщо ОК, false якщо Не ОК")
    comment: str = Field(description="Коментар із розбором")

def analyze_conversation(transcript_text, services_list):  
    system_instruction = f"""
    Ти — суворий професійний аудитор контролю якості телефонних дзвінків в автосервісі (СТО).
    Твоє завдання — проаналізувати діалог і повернути результат СТРОГО у форматі JSON за схемою.

    ПРАВИЛА ВИЗНАЧЕННЯ ТИПУ РОБІТ:
    Вибери ОДНЕ точне значення з цього списку: {services_list}.
    - Якщо клієнт звертається щодо автоелектрики, заміни фар, лампочок, ремонту кнопок, дооснащення або будь-яких інших механічних завдань, яких НЕМАЄ в списку — вибирай СТРОГО "Слюсарні роботи".
    - Якщо клієнт говорить про помилки на панелі приладів, чек (check engine), комп'ютерну перевірку — вибирай "Комп'ютерна діагностика".
    - Якщо клієнт говорить про стуки в ходовій частині, перевірку підвіски — вибирай "Комплексна діагностика підвіски".
    
    ПРАВИЛА ОЦІНЮВАННЯ ТА СТАТУСУ:
    - Постав is_ok = true (ОК), тільки якщо менеджер був ввічливим і зафіксував запис або знайшов альтернативу.
    - Постав is_ok = false (Не ОК), якщо менеджер «злив» клієнта.
    - Оцінка manager_rating ставиться від 1 до 5.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Проаналізуй цей діалог:\n{transcript_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=CallAnalysis,
                temperature=0.0
            ),
        )
        return json.loads(response.text)
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error {error_msg}")
                
    return None


def process_and_save_data(excel_path, audio_filename, transcript_text):
    analysis = analyze_conversation(transcript_text, services_list)
    
    clean_transcript = str(transcript_text).strip()

    target_columns = ["Транскрибація", "тип робіт", "чи є запис", "оцінка роботи менеджера"]
    
    if analysis:
        new_data = {
            "Транскрибація": clean_transcript,
            "тип робіт": analysis.get("job_type"),
            "чи є запис": "ОК" if analysis.get("is_ok") else "Не ОК",
            "оцінка роботи менеджера": analysis.get("manager_rating")
        }
    else:
        new_data = {
            "Транскрибація": clean_transcript,
            "тип робіт": "Помилка аналізу",
            "чи є запис": "Не перевірено",
            "оцінка роботи менеджера": "-"
        }

    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
        existing_targets = [col for col in target_columns if col in df.columns]

        if existing_targets:
            df = df[existing_targets]
        else:
            df = pd.DataFrame(columns=target_columns)
        
        if not df.empty and "Транскрибація" in df.columns:
            df["Транскрибація"] = df["Транскрибація"].astype(str).str.strip()
            marker = "".join(clean_transcript[:30].split()).lower()
            
            def match_marker(row_text):
                return "".join(str(row_text)[:30].split()).lower() == marker
            
            match_index = df[df["Транскрибація"].apply(match_marker)].index
            
            if not match_index.empty:
                for key, value in new_data.items():
                    df.loc[match_index[0], key] = value
                
                if len(match_index) > 1:
                    df = df.drop(match_index[1:])
                
             
                df = df.reindex(columns=target_columns)
                df = df.fillna("-")
                df.to_excel(excel_path, index=False)
                return

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    else:
        df = pd.DataFrame([new_data])

    df = df.reindex(columns=target_columns)
    df = df.fillna("-")
    df.to_excel(excel_path, index=False)

if __name__ == '__main__':

    EXCEL_PATH = r'F:\it\Python\files\Транскрибація1.xlsx'
    SAVE_DIR = r'F:\it\Python\files'  

    for file in os.listdir(SAVE_DIR):
        text_file = os.path.join(SAVE_DIR, file)
        
        if file.endswith('.txt') and os.path.isfile(text_file):
            file_content = None
            
            try:
                with open(text_file, "r", encoding="utf-8") as g:
                    file_content = g.read()
            except Exception as e:
                print(f"Error in {file}: {e}")
                continue 
            
            if file_content is not None:
                process_and_save_data(EXCEL_PATH, file, file_content)





