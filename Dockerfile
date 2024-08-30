ARG REGISTRY_PATH='harbor.devops.indico.io/indico'
ARG BUILD_TAG=latest

# builder stage
FROM ${REGISTRY_PATH}/ubuntu-2204-build:${BUILD_TAG} AS poetry-installer
ARG POETRY_INSTALL_ARGS
ARG GEMFURY_TOKEN

COPY pyproject.toml poetry.lock /venv/

RUN poetry export \
        -f requirements.txt \
        --output requirements.txt \
        --without-hashes  \
        --with dev && \
        ${POETRY_INSTALL_ARGS} && \
    pip3 install -r requirements.txt --no-deps


# image
FROM ${REGISTRY_PATH}/ubuntu-2204-deploy:${BUILD_TAG}
ENV PYTHONPATH="/aiohttp_responses"

WORKDIR /aiohttps_responses

COPY --from=poetry-installer /venv /venv
COPY . /aiohttps_responses/


CMD ["sleep", "infinity"]
