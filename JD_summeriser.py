import pandas as pd
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

# === Load JD CSV ===
df = pd.read_csv(r"C:\Users\vinay asish\OneDrive\Desktop\Accenture hackathon\job_description.csv", encoding="ISO-8859-1")

# Make sure the expected columns exist
if "Job Title" not in df.columns or "Job Description" not in df.columns:
    print(f"[❌] Required columns not found. Available columns: {list(df.columns)}")
    exit()


# === Step 2: Setup LLM ===
llm = Ollama(model="mistral")

# === Step 3: Prompt Template ===
prompt = PromptTemplate(
    input_variables=["job_name", "jd"],
    template="""
You are an AI assistant helping a recruiter.

Read and summarize the following job description into the following structured fields:

- **Required Skills** (as bullet points)
- **Experience Required**
- **Qualifications**
- **Job Responsibilities** (as bullet points)

Job Title: {job_name}
Job Description:
{jd}

Return only the structured summary, no extra explanation or commentary.
"""
)

# === Step 4: LangChain Chain Setup ===
chain = LLMChain(llm=llm, prompt=prompt)

# === Step 5: Run Summarizer for All Rows ===
summaries = []
for idx, row in df.iterrows():
    job_name = row["Job Title"]
    jd_text = row["Job Description"]
    
    print(f"\n📝 Summarizing JD #{idx + 1} - {job_name}...\n")
    try:
        summary = chain.run(job_name=job_name, jd=jd_text)
        summaries.append(summary)
    except Exception as e:
        print(f"[❌] Failed to summarize row {idx}: {e}")
        summaries.append("Error during summarization")


# === Step 6: Save Output ===
df["JD Summary"] = summaries
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df.to_csv("jd_summary_output.csv", index=False)
print("\n✅ All done! Saved summaries to 'jd_summary_output.csv'")