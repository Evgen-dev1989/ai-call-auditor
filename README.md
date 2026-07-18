# 📊 AI-Auditor: Automated CRM Call Analysis via Gemini API

A Python-based automated Quality Assurance (QA) system for automotive service centers (STOs). The pipeline reads text transcripts of telephone conversations between service managers and clients, processes them using Google's Gemini LLM (`gemini-2.5-flash`), maps the requests to a strict list of workshop services, evaluates manager performance, and outputs structured analytical reports directly into an Excel spreadsheet.

## 🚀 Key Features

* **Intelligent Service Mapping**: The system extracts the core customer intent from casual or chaotic dialogs and maps it to a strict pre-defined array of workshop services (e.g., *Комп'ютерна діагностика*, *Слюсарні роботи*, *Комплексна діагностика підвіски*).
* **Automated Quality Assurance (QA)**: Acts as an unbiased, rigorous auditor. It evaluates whether the manager actively attempted to close the booking, remained polite, handled objections, or offered alternative dates, scoring them on a 1-5 scale.
* **Radical Deduplication Engine**: Features an advanced anti-duplication logic based on content marker matching (the first 30 normalized characters of the text). Re-running the script updates existing logs with fresh AI analyses instead of creating redundant rows.
* **Fault-Tolerant Retry Policy**: Fully handles Google API server instabilities (`503 Unavailable`) and rate limits (`429 Resource Exhausted`). It dynamically parses the cooldown period requested by the Free Tier limits and triggers an intelligent `time.sleep()`, preventing loop crashes during batch processing.
* **Excel Layout Auto-Correction**: Automatically drops old, corrupted, or misaligned columns on the fly, forcing the table layout to strictly adhere to the 4 target analytical fields.

---

## 🛠 Excel Report Structure

The generated spreadsheet (`Транскрибація.xlsx`) maintains a clean, normalized layout consisting of exactly 4 columns:

| Column (A) | Column (B) | Column (C) | Column (D) |
| :--- | :--- | :--- | :--- |
| **Транскрибація** | **тип робіт** | **чи є запис** | **оцінка роботи менеджера** |
| *Dialogue transcript text...* | Слюсарні роботи | Не ОК | 3 |
| *Dialogue transcript text 2...* | Комп'ютерна діагностика | ОК | 5 |

