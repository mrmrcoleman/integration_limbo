FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install the required dependencies
RUN pip install -r requirements.txt
RUN pip install .

# Remove the source code after installation
RUN rm -rf /app/integration_limbo