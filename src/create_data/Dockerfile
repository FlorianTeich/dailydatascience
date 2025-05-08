# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the required Python package 'uv'
RUN pip install --no-cache-dir uv

# copy pyproject.toml
COPY pyproject.toml /app
# Install the required Python packages

RUN uv sync --group create_data
#RUN uv pip install --group train

# Command to run the script using 'uv'
CMD ["uv", "run", "create_data.py"]
