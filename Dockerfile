FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Setting this accepts the XTTS-v2 model license (non-commercial use) so the
# model can download without a prompt. Remove it if you don't agree.
ENV COQUI_TOS_AGREED=1
ENV GRADIO_SERVER_NAME=0.0.0.0

# Bake the model into the image so containers start without downloading it.
RUN python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"

COPY app.py .

CMD ["python", "app.py"]
