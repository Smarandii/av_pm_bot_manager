FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app/

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "./am_pm_bot/main.py"]