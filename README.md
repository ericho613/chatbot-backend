# ChatbotBackend

## Creating the environment

To set up the environment and install the project dependencies, run the following commands:

```bash
# Navigate to the project folder
cd /chatbot-backend

# Create the virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate

# Install the project dependencies in the virtual environment
pip3 install -r requirements.txt
```

## Running the application

To start the application locally, run the following commands:

```bash
# Navigate to the project folder
cd /chatbot-backend

# Activate the virtual environment
venv\Scripts\activate

# Run the application using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

To reload the application, run the following command:

```bash
uvicorn app.main:app --reload --port 8000
```

Alternatively, to use Docker to run the app, run the following commands:

```bash
# Navigate to the project folder
cd /chatbot-backend

# Build the application in the Docker container
docker compose build --no-cache

# Start the built application in the Docker container
docker compose up -d
```

To stop the Docker container and the running application, run the following command:

```bash
docker compose down
```

