# Base Image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

#Copying requirements file
COPY requirements.txt .

#Installing Dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copying the source code
COPY . .

# Exposing the port
EXPOSE 8000

# Running the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

