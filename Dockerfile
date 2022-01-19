FROM python:3.8

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt --default-timeout=100

ENV FLASK_APP=application.py

CMD [ "flask", "run", "--host=0.0.0.0"]