from fastapi import FastAPI
from dotenv import load_dotenv
import pandas as pd
import os
from datetime import datetime
from app.agents.orchestrator import LLMDataCleaningAgent

load_dotenv()

app = FastAPI()


@app.post("/clean")
def clean_dataset(file_name: str):

    raw_path = f"data/raw/{file_name}"

    if not os.path.exists(raw_path):
        return {"error": "File not found"}

    df = pd.read_csv(raw_path)

    agent = LLMDataCleaningAgent()

    cleaned_df, plan, audit_log = agent.run(df)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_path = f"data/cleaned/cleaned_{timestamp}_{file_name}"
    cleaned_df.to_csv(cleaned_path, index=False)

    return {
        "cleaned_file": cleaned_path,
        "cleaning_plan": plan,
        "audit_log": audit_log
    }
