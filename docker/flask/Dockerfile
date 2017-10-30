FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN groupadd -r flask && useradd -r -g flask flask

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /app/src

COPY ./docker/flask/gunicorn.sh /gunicorn.sh
COPY ./docker/flask/entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /entrypoint.sh \
    && chown flask /entrypoint.sh \
    && chmod +x /gunicorn.sh \
    && chown flask /gunicorn.sh

WORKDIR /app/src

ENTRYPOINT ["/entrypoint.sh"]
