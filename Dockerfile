FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway sets PORT env var dynamically)
ENV PORT=8080
EXPOSE 8080

# Use shell form so $PORT expands at runtime
CMD gunicorn app:app --bind 0.0.0.0:${PORT} --workers 2 --timeout 120
