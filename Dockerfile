FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Optional: legacy map data (blog mode ignores items_data.json at runtime)
RUN python script/build_data.py || true

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 120 app:app
