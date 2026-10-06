# 1. Base Image: Python 3.11 lightweight Linux
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy backend source code
COPY . .

# 5. Expose FastAPI port
EXPOSE 8000

# 6. Start FastAPI server using standard uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
