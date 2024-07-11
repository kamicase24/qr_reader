FROM python:3.8-slim

WORKDIR /app

COPY compose/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

RUN python -m venv venv
RUN . venv/bin/activate

ENV FLASK_APP=app.py

CMD ["sh", "-c", ". venv/bin/activate && flask run --host=0.0.0.0"]