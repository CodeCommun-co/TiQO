FROM python:3.10-bullseye

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -
ENV PATH="/etc/poetry/bin:$PATH"

WORKDIR /TiQO
# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install
RUN poetry --version

# Run your app
#COPY . /app
#CMD [ "poetry", "run", "python", "-c", "print('Hello, World!')" ]