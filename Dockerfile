FROM python:3.11-alpine as final
FROM python:3.11-alpine as build

RUN apk add git
COPY . /usr/src/solarmax2mqtt
RUN cd /usr/src/solarmax2mqtt && pip wheel .

FROM final

COPY --from=build /usr/src/solarmax2mqtt/*.whl /tmp/
RUN cd /tmp &&  \
    PYTHONDONTWRITEBYTECODE=1 pip install --no-compile --no-cache-dir --no-deps *.whl && \
    rm /tmp/*.whl

CMD ["python", "-m", "solarmax2mqtt.docker_main"]
