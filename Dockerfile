FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app/

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]