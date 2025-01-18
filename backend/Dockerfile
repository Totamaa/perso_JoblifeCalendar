FROM python:3.13.1 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --target /app/dependencies

FROM python:3.13.1-slim

WORKDIR /app

COPY --from=builder /app/dependencies /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--workers", "2",]
