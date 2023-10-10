# pin python version to 3.11
FROM python:3.11

# Set the working project directory
WORKDIR thermoGuard/

# Copy requirements.txt to the root level of the directory
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local files into the docker project directory
COPY . .

# Update the shell script permission to the executable
RUN chmod +x script.sh

# Expose the PORTS for the UVICORN web server and uAGent Bureau
EXPOSE 8080
EXPOSE 5050

# Run the Python module file
CMD ["python", "-m", "src.main"]
