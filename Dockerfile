FROM python:3.12

RUN wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
RUN echo "deb [arch=all,amd64 signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr lunar" | tee /etc/apt/sources.list.d/prebuilt-mpr.list

RUN apt update && apt install -y just clang

RUN pip install --upgrade pip

WORKDIR /app

COPY .python-version pyproject.toml poetry.lock /app/

ENV POETRY_HOME=/poetry

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/poetry/bin:${PATH}"

RUN poetry install

ENTRYPOINT bash
