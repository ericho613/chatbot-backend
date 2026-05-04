To run:

cd /opt/chatbot-backend
python -m venv venv
venv/bin/activate
pip3 install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000


To reload:

uvicorn app.main:app --reload --port 8000