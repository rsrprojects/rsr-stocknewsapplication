# Use a base image that includes Python 3
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the application's requirements file
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the port your application will run on (if applicable)
EXPOSE 5000

# Command to run the application (if applicable)
# CMD ["python", "app.py"]