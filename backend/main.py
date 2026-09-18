from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "postgresql+psycopg://esp32_user:esp32@localhost:5432/esp32_db"

engine = create_engine(DATABASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SensorData(BaseModel):
    light_level: float

@app.post("/api/sensor")
def save_sensor_data(data: SensorData):
    with engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO sensor_data (light_level)
                VALUES (:light_level)
            """),
            {
                "light_level": data.light_level,
            }
        )

    return {"status": "ok"}

@app.get("/api/sensor/latest")
def get_sensor_data():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM sensor_data
                ORDER BY created_at DESC
                LIMIT 1
            """)
        )

        return result.mappings().first()

@app.get("/api/sensor")
def get_sensor_data():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM sensor_data
                ORDER BY id DESC
            """)
        )

        return result.mappings().all()