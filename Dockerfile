FROM python:3.11-alpine

WORKDIR /PERCEPTRONX

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconf

COPY Backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /PERCEPTRONX/Frontend_Web/static/assets/images/user

RUN chmod -R 777 /PERCEPTRONX/Frontend_Web/static/assets/images/user

WORKDIR /PERCEPTRONX/Backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]