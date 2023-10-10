FROM python:3.11

# Copy the script file
WORKDIR thermoGuard/

COPY requirements.txt .

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

# Create a virtual environment
COPY . .

# Copy environment variables
ENV WEATHER_API_KEY "b45b0576a0834094b9380951230110"

# Update the shell script permission to executable
RUN chmod +x script.sh

EXPOSE 8080
EXPOSE 5050

# Run the script file
CMD ["python", "-m", "src.main"]