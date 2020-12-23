FROM python:3-alpine

RUN apk update && apk add libpq
RUN apk update && apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN apk add --no-cache python3-dev libffi-dev gcc && pip3 install --upgrade pip
RUN apk add --no-cache jpeg-dev zlib-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
RUN mv wait-for /bin/wait-for

RUN pip install --no-cache-dir -r requirements.txt
RUN apk del .build-deps

EXPOSE 8000

CMD ["gunicorn", "mysite.wsgi", "0:8000"]