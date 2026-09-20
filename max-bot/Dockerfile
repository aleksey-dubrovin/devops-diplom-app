# =============================================================================
# MAX Bot: приём webhook от Alertmanager
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY max_bot.py .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "max_bot.py"]