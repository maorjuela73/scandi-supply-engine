FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m textblob.download_corpora

COPY . .
CMD ["python", "run.py"]