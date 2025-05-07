FROM python:3.12-slim

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

# 시스템 라이브러리 (Playwright + Headless Chromium용)
RUN apt-get update && apt-get install -y \
    wget ca-certificates libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libxss1 libasound2 libxcomposite1 libxdamage1 libxrandr2 \
    libx11-xcb1 libxkbcommon0 libdrm2 libgbm1 libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# pipenv 설치 후 의존성 설치
RUN pip install --upgrade pip pipenv
RUN pipenv install --deploy --system

# Playwright 브라우저 설치
RUN python -m playwright install --with-deps

CMD ["python", "src/main.py"]
