FROM python:3.14.7-alpine

WORKDIR /app

RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev \
    && apk add --no-cache libpq

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt \
    && apk del .build-deps

COPY . .

RUN adduser -D appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
