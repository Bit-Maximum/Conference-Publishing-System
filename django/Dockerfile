# Base build stage
FROM python:3.12-slim-bookworm AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim-bookworm

RUN useradd -m -r django-user && \
   mkdir /app && \
   chown -R django-user /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=django-user:django-user . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER django-user

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "publisher.wsgi:application"]

ENTRYPOINT ["/app/entrypoint.sh"]