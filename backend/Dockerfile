FROM python:3.12-slim

WORKDIR /srv
COPY backend/requirements.txt backend/requirements-ml.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r backend/requirements.txt \
 && pip install --no-cache-dir -r backend/requirements-ml.txt
COPY backend/ ./backend/
COPY config/ ./config/
COPY prompts/ ./prompts/
ENV PYTHONPATH=/srv/backend UPLOAD_ROOT=/data/uploads
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
