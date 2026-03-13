FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./generator/src/

RUN touch ./generator/__init__.py

CMD ["python", "-m", "generator.src.producer"]