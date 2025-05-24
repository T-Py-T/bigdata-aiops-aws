FROM bitnami/spark:3.3.0-debian-11-r0
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
CMD ["python", "realtime_processor.py"]
