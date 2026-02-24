FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "gunicorn bot:app --bind 0.0.0.0:8080"]
```

**`requirements.txt`** — pin to known-working versions on Python 3.11:
```
python-telegram-bot==20.6
Flask==2.3.3
gunicorn==21.2.0
