FROM python:3.10

LABEL version="0.2.2"
LABEL author="indico"
LABEL email="engineering@indicodata.ai"
LABEL description="proper aiohttp_responses lib"

ENV PATH=/aiohttp_responses/bin:/usr/local/bin:${PATH} \
    POETRY_HOME="/usr/local"

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . /aiohttp_responses
WORKDIR /aiohttp_responses

RUN poetry install --no-interaction --no-ansi --with dev

CMD ["sleep", "infinity"]
