FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd -r peacloud && useradd -r -g peacloud -d /app peacloud
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=peacloud:peacloud app ./app
USER peacloud
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/liveness',timeout=2)"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--workers","2"]
