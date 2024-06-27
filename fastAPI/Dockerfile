# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

# Run app.py when the container launches
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
