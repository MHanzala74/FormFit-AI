# Runs the Streamlit video-analysis app (no webcam/audio needed).
#   docker build -t formfit-ai .
#   docker run --rm -p 8501:8501 formfit-ai
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir ".[web]"

EXPOSE 8501
CMD ["streamlit", "run", "src/formfit/app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
