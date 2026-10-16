FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends nodejs sqlite3 && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /work
CMD ["python3", "--version"]
