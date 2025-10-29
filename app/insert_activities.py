# app/activity_adding.py

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import json
from app.models import Base, Activity
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://neondb_owner")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

excel_file = os.path.join(
    os.path.dirname(__file__), "redflag_activities_structured.xlsx"
)
df = pd.read_excel(excel_file)

for _, row in df.iterrows():
    try:
        desc = row.get("description_content")
        if isinstance(desc, str):
            try:
                desc = json.loads(desc)
            except json.JSONDecodeError:
                desc = {"text": desc}

        activity = Activity(
            activity_id=str(uuid.uuid4()),
            red_flag=str(row["red_flags"]),
            step_order=int(row["levels"]),
            duration_days=10,
            duration_minutes=int(row["duration_minutes"]),
            content_jsonb=desc,
            alternatives=["Future implementation"],
            # sequence_order=int(row["sequence_order"]),
            version=row.get("version", "v1.0"),
            created_by=row.get("created_by_system", "system"),
        )

        session.add(activity)
    except Exception as e:
        print(f"❌ Error adding row {row.to_dict()}: {e}")

try:
    session.commit()
    print("✅ Data imported successfully!")
except Exception as e:
    session.rollback()
    print("❌ Commit failed:", e)
finally:
    session.close()
