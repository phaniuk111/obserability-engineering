FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY telemetry.py shop.py ./
ENV PYTHONUNBUFFERED=1
CMD ["python", "shop.py"]
