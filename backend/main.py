from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
from datetime import datetime, timedelta
import math
import csv

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 샘플 비행 데이터 (각 ID별 1분 동안 1초 간격, 원형 경로 생성)
sample_data = {}
start_times = {i: datetime(2025, 6, 1, 8, 0, 0) + timedelta(hours=i-1) for i in range(1, 6)}
centers = {
    1: (37.5665, 126.9780),
    2: (37.5675, 126.9790),
    3: (37.5685, 126.9800),
    4: (37.5695, 126.9810),
    5: (37.5705, 126.9820),
}
for flight_id, start in start_times.items():
    entries = []
    center_lat, center_lon = centers[flight_id]
    radius = 0.0001 * flight_id
    for sec in range(60):
        angle = math.radians(sec * 6)
        lat = center_lat + radius * math.cos(angle)
        lon = center_lon + radius * math.sin(angle)
        timestamp = (start + timedelta(seconds=sec)).isoformat() + "Z"
        entries.append({
            # 시간은 내부 생성용이므로 반환 데이터에서 제외
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude": round(100 + 5 * math.sin(angle) + flight_id, 1),
        })
    sample_data[flight_id] = entries

# tmp 디렉터리 생성
tmp_dir = "./tmp"
os.makedirs(tmp_dir, exist_ok=True)

@app.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    file_path = os.path.join(tmp_dir, file.filename)
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 저장 실패: {e}")
    try:
        os.remove(file_path)
    except OSError:
        pass
    await asyncio.sleep(10)
    return JSONResponse(content={"message": "파일 분석이 완료되었습니다."})

@app.get("/data/{item_id}")
async def get_flight_data(item_id: int):
    # item_id 6번: output.csv에서 읽어오기
    if item_id == 6:
        csv_path = "./output.csv"
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="output.csv 파일을 찾을 수 없습니다.")
        results = []
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 'latitude' in row and 'longitude' in row:
                        results.append({
                            'latitude': float(row['latitude']),
                            'longitude': float(row['longitude'])
                        })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CSV 읽기 실패: {e}")
        if not results:
            raise HTTPException(status_code=404, detail="CSV에 유효한 데이터가 없습니다.")
        return results

    # 그 외 ID: 샘플 데이터
    data = sample_data.get(item_id)
    if data is None:
        raise HTTPException(status_code=404, detail="해당 비행 데이터가 없습니다.")
    return data

# uvicorn 실행 예시:
# uvicorn flight_api:app --reload --host 0.0.0.0 --port 8000
