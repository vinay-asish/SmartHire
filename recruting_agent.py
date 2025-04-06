import os
import json
import sqlite3
import fitz  # PyMuPDF for reading PDFs
import time
import logging
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_ollama import OllamaLLM


# === CONFIG ===
CV_FOLDER = "./CVs1"
MODEL_NAME = "mistral"
DB_PATH = "recruitment.db"

# === Setup Logging ===
logging.basicConfig(filename='recruiting_errors.log', level=logging.ERROR)

# === Setup LLM ===
llm = OllamaLLM(model=MODEL_NAME)

# === Prompts ===
extract_prompt = PromptTemplate(
    input_variables=["cv_text"],
    template="""
Extract this info from the CV:

- Full Name
- Email
- Education (list)
- Work Experience (role, company, duration)
- Skills (list)
- Certifications (list)

Return JSON format only.

CV:
{cv_text}
"""
)
extract_chain = LLMChain(llm=llm, prompt=extract_prompt)

score_prompt = PromptTemplate(
    input_variables=["jd", "cv_info"],
    template="""
You are a strict evaluator. ONLY respond in proper JSON. No markdown, no preface.

Job Description:
{jd}

Candidate Info:
{cv_info}

Your output must be:
{{
  "Match score": number from 0 to 100,
  "Short reasoning": "brief explanation"
}}

Strict JSON only. Do not add anything before or after. No bullet points. No commentary.
"""

)
score_chain = LLMChain(llm=llm, prompt=score_prompt)

# === Retry Helper ===
def retry_chain(chain, inputs, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = chain.run(**inputs)
            return json.loads(response)
        except json.JSONDecodeError:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

# === Ensure candidates table exists ===
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    cv_path TEXT,
    parsed_data TEXT,
    match_score INTEGER,
    reasoning TEXT,
    jd_id INTEGER
)
""")
conn.commit()

# === Load all JD summaries ===
c.execute("SELECT id, summary FROM jobs")
jd_entries = c.fetchall()

if not jd_entries:
    raise Exception("No job descriptions found in DB")

# === Process CV PDFs ===
for filename in os.listdir(CV_FOLDER):
    if not filename.endswith(".pdf"):
        continue

    filepath = os.path.join(CV_FOLDER, filename)
    print(f"\n📄 Processing: {filename}")

    try:
        with fitz.open(filepath) as doc:
            cv_text = "\n".join([page.get_text() for page in doc])

        print(f"📄 CV length: {len(cv_text)}")
        if len(cv_text.strip()) == 0:
            print(f"❌ Empty CV text in {filename}")
            continue

        try:
            extracted_json = retry_chain(extract_chain, {"cv_text": cv_text})
        except Exception as e:
            logging.error(f"JSON extraction failed for {filename}: {e}", exc_info=True)
            continue

        if not extracted_json.get("Email"):
            print(f"⚠️ Missing email in extracted data for {filename}")

        extracted_json["Skills"] = list(set(skill.lower() for skill in extracted_json.get("Skills", [])))

        print(f"✅ Parsed {extracted_json.get('Full Name', 'Unknown')}")

        for jd_id, jd_summary in jd_entries:
            # Check for duplicates
            c.execute("SELECT COUNT(*) FROM candidates WHERE email = ? AND jd_id = ?", (
                extracted_json.get("Email", "Not found"),
                jd_id
            ))
            if c.fetchone()[0]:
                print(f"⚠️ Duplicate entry skipped for {extracted_json.get('Email')}, JD {jd_id}")
                continue

            try:
                score_json = retry_chain(score_chain, {"jd": jd_summary, "cv_info": json.dumps(extracted_json)})
            except Exception as e:
                logging.error(f"Scoring failed for {filename} against JD {jd_id}: {e}", exc_info=True)
                continue

            print(f"🧪 Raw score JSON: {score_json}")
        
            match_score = score_json.get("Match score", 0)
            reasoning = score_json.get("Short reasoning", "")

            print(f"📥 Inserting candidate: {extracted_json.get('Full Name')} | Score: {match_score}")

            c.execute("""
                INSERT INTO candidates (name, email, cv_path, parsed_data, match_score, reasoning, jd_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                extracted_json.get("Full Name", "Unknown"),
                extracted_json.get("Email", "Not found"),
                filename,
                json.dumps(extracted_json),
                match_score,
                reasoning,
                jd_id
            ))
            conn.commit()

            if match_score >= 80:
                print(f"🎯 Match with JD {jd_id}: Score {match_score} ✅ Suitable")
            else:
                print(f"➖ Match with JD {jd_id}: Score {match_score}")

    except Exception as e:
        logging.error(f"Failed on {filename}: {e}", exc_info=True)

# === Export results to CSV ===
df = pd.read_sql_query("SELECT * FROM candidates", conn)
print(f"🔍 Found {len(df)} candidates in DB.")
df.to_csv("candidates_summary.csv", index=False)

conn.close()
print("\n✅ All CVs processed and saved to DB.")