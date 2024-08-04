# Use an official Python runtime as a parent image
FROM python:3.12.4-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG FIREBASE_CREDENTIALS
ENV FIREBASE_CREDENTIALS=$FIREBASE_CREDENTIALS

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* /code/

# Copy the project
COPY storytopia_backend /code/storytopia_backend

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Command to run the application
CMD ["uvicorn", "storytopia_backend.main:app", "--host", "0.0.0.0", "--port", "8080"]