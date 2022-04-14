FROM python:3.10

LABEL version="0.2.2"
LABEL author="indico"
LABEL email="engineering@indicodata.ai"
LABEL description="proper aiohttp_responses lib"

ENV PATH=/aiohttp_responses/bin:/root/.poetry/bin:${PATH}

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

COPY . /aiohttp_responses
WORKDIR /aiohttp_responses

# no need for virtualenv in docker
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["bash"]
