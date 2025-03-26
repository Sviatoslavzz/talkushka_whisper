FROM python:3.12

WORKDIR /talkushka-transcriber

COPY cert/ /talkushka-transcriber/cert
COPY src/ /talkushka-transcriber/src
COPY pyproject.toml /talkushka-transcriber

RUN pip install --upgrade pip && pip install --no-cache-dir . -U

ENTRYPOINT ["talksuhka-transcriber"]
