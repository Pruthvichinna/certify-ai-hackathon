# Use an official lightweight Python image.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file and install the dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container.
COPY . .

# Tell the container what command to run when it starts.
# This runs your Flask app using the Gunicorn server on port 8080.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]