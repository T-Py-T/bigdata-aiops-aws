# services/ray_ml_processor/Dockerfile
# Builds Ray ML processor container with Kafka integration
# Installs: Ray cluster client, Kafka consumer/producer, ML dependencies

FROM rayproject/ray:2.9.0-py310

WORKDIR /app

# Install additional dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/ml_processor.py"]

