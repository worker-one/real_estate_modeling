# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the backend and frontend directories into the container
COPY backend /app/backend
COPY frontend /app/frontend

# Install backend dependencies
RUN pip install --upgrade pip
WORKDIR /app/backend
RUN pip install .

# Install frontend dependencies
WORKDIR /app/frontend
RUN pip install .

# Go back to the root directory
WORKDIR /app

# Expose the ports for backend and frontend
EXPOSE 8000 8501

# Start the backend and frontend services
CMD ["sh", "-c", "python backend/src/app/api/main.py --port 8000 & python frontend/src/app/main.py --server.port 8501 --server.address 0.0.0.0"]