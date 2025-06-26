# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /app

# Install system libraries required by WeasyPrint (Cairo, Pango, GDK-PixBuf)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libffi-dev \
        shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Enable PDF generation feature by default inside the container
ENV PDF_ENABLED=true

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
