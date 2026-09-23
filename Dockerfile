FROM python:3.11-slim

# Install ffmpeg (required for merging video/audio and audio extraction)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render sets $PORT automatically; default to 5000 for local runs
ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "python app.py"]
