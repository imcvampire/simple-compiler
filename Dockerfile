FROM python:3.12.1

# We are going to use the latest available pip. Not necessary for poetry issue
RUN pip install --upgrade pip

WORKDIR /app

COPY .python-version pyproject.toml poetry.lock /app/
# Poetry will be installed to that location
ENV POETRY_HOME=/poetry

# We ship get-poetry.py with us rather then downloading it. You can get it the way it suits you.
RUN curl -sSL https://install.python-poetry.org | python3 -


# Looks like poetry fails to add itself to the Path in Docker. We add it here.
ENV PATH="/poetry/bin:${PATH}"

# Use secret to get packages from the private repo
RUN poetry install

ENTRYPOINT bash
