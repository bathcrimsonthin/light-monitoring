from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "postgresql+psycopg://esp32_user:esp32@localhost:5432/esp32_db"

engine = create_engine(DATABASE_URL)

connected_clients: list[WebSocket] = []

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
async def save_sensor_data(data: SensorData):
    with engine.begin() as connection:
        result = connection.execute(
            text("""
                INSERT INTO sensor_data (light_level)
                VALUES (:light_level)
                RETURNING *
            """),
            {
                "light_level": data.light_level,
            }
        )

        new_data = result.mappings().first()

    # WebSocket接続中のクライアントに送信
    for client in connected_clients:
        await client.send_json(jsonable_encoder(dict(new_data)))

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

@app.websocket("/ws/sensor")
async def websocket_sensor(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    # 現在の最新データを取得
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT *
                FROM sensor_data
                ORDER BY created_at DESC
                LIMIT 1
            """)
        )

        latest_data = result.mappings().first()

    # 最新データを送信
    if latest_data is not None:
        await websocket.send_json(jsonable_encoder(dict(latest_data)))

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.remove(websocket)