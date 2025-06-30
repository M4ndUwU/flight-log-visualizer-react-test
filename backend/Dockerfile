# backend/Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app

# 1) OS 패키지 설치 & 캐시 정리
RUN apt-get update \
 && rm -rf /var/lib/apt/lists/*

# 2) requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) 소스 복사
COPY . .

# 4) 개발용 uvicorn 설정
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
