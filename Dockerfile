# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Install Pipenv
RUN pip install -U pipenv

# Copy Pipfile and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /app/

# Install dependencies using Pipenv
RUN pipenv install --deploy --system

# Copy the rest of the application files to the container
COPY . /app/

# Expose port 5001 for Gunicorn
EXPOSE 5001

# Run Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:create_app()"]