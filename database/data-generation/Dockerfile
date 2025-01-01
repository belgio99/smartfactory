# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script and .env file into the container
COPY log_generator.py .
COPY .env .

# Command to run the script
CMD ["python", "log_generator.py"]