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
    job_type: str = Field(description="Выбранный тип работ из списка")
    manager_rating: int = Field(description="Оценка от 1 до 5")
    is_ok: bool = Field(description="true если ОК, false если Не ОК")
    comment: str = Field(description="Комментарий с разбором")

def analyze_conversation(transcript_text, services_list):  # Увеличили число попыток до 5
    system_instruction = f"""
    Ты — строгий профессиональный аудитор контроля качества телефонных звонков в автосервисе (СТО).
    Твоя задача — проанализировать диалог и вернуть результат СТРОГО в формате JSON по схеме.

    ПРАВИЛА ОПРЕДЕЛЕНИЯ ТИПА РАБОТ:
    Выбери ОДНО точное значение из этого списка: {services_list}.
    - Если клиент обращается по поводу автоэлектрики, замены фар, лампочек, ремонта кнопок, дооснащения или любых других механических задач, которых НЕТ в списке — выбирай СТРОГО "Слюсарні роботи".
    - Если клиент говорит об ошибках на панели, чеке, компьютерной проверке — выбирай "Комп'ютерна діагностика".
    - Если клиент говорит о стуках в ходовой, проверке подвески — выбирай "Комплексна діагностика підвіски".
    
    ПРАВИЛА ОЦЕНКИ И СТАТУСА:
    - Поставь is_ok = true (ОК), только если менеджер был вежлив и зафиксировал запись/нашел альтернативу.
    - Поставь is_ok = false (Не ОК), если менеджер «слил» клиента.
    - Оценка manager_rating ставится от 1 до 5.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Проанализируй этот диалог:\n{transcript_text}",
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


