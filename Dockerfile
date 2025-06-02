# Use a slim Python base image for efficiency
FROM python:3.10-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files
# and to ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install any system dependencies your app might need (optional for this simple app)
# Uncomment and add if you use PostgreSQL (libpq-dev) or other native libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
# This step is done separately to leverage Docker's caching for faster builds
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Expose the port that Django will run on (default for dev server)
EXPOSE 8000

# Command to run the Django application
# This will first run migrations and then start the development server.
# For production, you'd use a WSGI server like Gunicorn here.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
