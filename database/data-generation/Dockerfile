# Use official Python image
FROM python:3.9-slim

COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script
CMD ["python", "log_generator.py"]