FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -r peacloud
USER peacloud
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
