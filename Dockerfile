FROM python:3.11

# Copy the script file
WORKDIR thermoGuard/

COPY requirements.txt .

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Create a virtual environment
COPY . .

# Update the shell script permission to executable
RUN chmod +x script.sh

EXPOSE 8080
EXPOSE 5050

# Run the script file
CMD ["python", "-m", "src.main"]