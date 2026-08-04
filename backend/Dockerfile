FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV ML_MODELS_DIR=/ml-models
ENV CLUSTER_PROFILES_PATH=/ml-models/cluster_profiles.json
ENV MARKET_VALUE_FEATURES_PATH=/ml-models/market_value_feature_names.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]