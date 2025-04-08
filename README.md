
# 🧠 AI-Powered Recruitment Automation System

This project is an end-to-end recruitment automation system powered by Large Language Models (LLMs). It streamlines the hiring process by summarizing job descriptions, parsing candidate CVs, scoring candidate-job matches, and automating interview scheduling.

## 🚀 Features

- **JD Summarization**: Converts unstructured job descriptions into structured summaries using the Mistral model via LangChain.
- **CV Parsing**: Extracts structured candidate data (skills, education, experience) from PDF CVs using LLMs.
- **Match Scoring**: Computes match scores between candidate profiles and job requirements with reasoning.
- **Database Integration**: Stores candidate and job data in a persistent SQLite database.
- **Interview Scheduling**: Sends personalized interview invitation emails to top-matching candidates.
- **Multi-Agent Workflow**: Modular scripts handle each part of the process independently.

## 🛠️ Tech Stack

- **Python**
- **LangChain** + **Ollama** (Mistral model)
- **SQLite** for lightweight persistent storage
- **PyMuPDF (fitz)** for PDF parsing
- **smtplib** for email automation

## 📂 Modules Overview

| Module | Description |
|--------|-------------|
| `JD_summeriser.py` | Summarizes job descriptions and stores structured data |
| `create_jobs_table.py` | Populates the jobs table from summarized JDs |
| `candidates_table.py` | Initializes the candidates database table |
| `recruting_agent.py` | Parses CVs, scores candidates, inserts into DB |
| `interview_scheduler.py` | Sends interview emails to shortlisted candidates |

## 🗃️ Database Schema

**`jobs` Table**  
- `id` (int, primary key)  
- `title` (text)  
- `summary` (text)

**`candidates` Table**  
- `id`, `name`, `email`, `cv_path`, `parsed_data`, `match_score`, `reasoning`, `jd_id`, `notified`

## 📌 Setup Instructions

1. Install dependencies:
   ```bash
   pip install langchain pandas pymupdf sqlite3
   ```

2. Make sure **Ollama** and the **Mistral model** are running:
   ```bash
   ollama run mistral
   ```

3. Place job descriptions in `job_description.csv`.

4. Run:
   ```bash
   python JD_summeriser.py
   python create_jobs_table.py
   python candidates_table.py
   python recruting_agent.py
   python interview_scheduler.py
   ```

5. Place all candidate CVs in the `CVs1` folder.

## 📈 Output

- `jd_summary_output.csv`: Structured JD summaries  
- `candidates_summary.csv`: Parsed and scored candidate data  
- Emails automatically sent to top-matching candidates

## 📬 Note

Update the sender email and credentials in `interview_scheduler.py` before running.



🧠 Built with LLMs to reimagine recruitment workflows!
```

---

Let me know if you want to add screenshots, a Streamlit UI section, or deployment instructions.
