FROM --platform=linux/x86_64 python:3.10.9-slim

WORKDIR /app

COPY ../requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ../config /app/config/
COPY ../src /app/src/
COPY ../plane.jpg /app/plane.jpg

EXPOSE 80

CMD ["streamlit", "run", "--server.port=80", "--server.fileWatcherType=none", "src/webapp.py"]