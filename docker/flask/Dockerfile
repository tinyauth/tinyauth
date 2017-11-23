FROM node AS jsbuilder

COPY admin/package.json /src/package.json
RUN cd /src && npm install

COPY admin/public /src/public
COPY admin/src /src/src
RUN cd /src && npm run build

FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN groupadd -r flask && useradd -r -g flask flask

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . /app/src
RUN pip install -r /app/src/requirements.txt -e /app/src

COPY --from=jsbuilder /src/build/asset-manifest.json /app/react/asset-manifest.json
COPY --from=jsbuilder /src/build/static /app/react/static

COPY ./docker/flask/gunicorn.sh /gunicorn.sh
COPY ./docker/flask/entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r//' /entrypoint.sh \
    && sed -i 's/\r//' /gunicorn.sh \
    && chown flask /entrypoint.sh \
    && chown flask /gunicorn.sh

WORKDIR /app/src

USER flask
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/gunicorn.sh"]
