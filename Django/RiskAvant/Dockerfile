# Dockerfile

# Python slim image
FROM python:3.13-slim

# Setting up environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installing system-level dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    pango1.0-tools \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libglib2.0-0 \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Seting the working directory
WORKDIR /app

# Copying the project files
COPY . /app/

# Installing Python dependencies for the project
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposing port on which service is to be run
EXPOSE 8000

# Starting the Django server - command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
