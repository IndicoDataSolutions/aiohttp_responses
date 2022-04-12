FROM python:3.10

LABEL version="0.1.0"
LABEL author="indico"
LABEL email="engineering@indicodata.ai"
LABEL description="proper aioresponses lib"

ENV PATH=/aioresponses/bin:/root/.poetry/bin:${PATH}

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

COPY . /aioresponses
WORKDIR /aioresponses

# no need for virtualenv in docker
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

CMD ["bash"]
