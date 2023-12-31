# First stage: Full Python image with build tools
FROM ubuntu:latest

# Install picamera2
RUN apt update
RUN apt install -y python3-libcamera python3-kms++
RUN apt install -y python3-prctl libatlas-base-dev ffmpeg libopenjp2-7 python3-pip

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry==1.4.2

# Set the working directory to /app
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN touch README.md


ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN poetry install

WORKDIR /app

COPY src ./src

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["poetry", "run", "python", "src/app.py"]