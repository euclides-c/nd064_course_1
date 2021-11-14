FROM python:2.7-alpine3.11

LABEL maintainer="Euclides Chauque"

WORKDIR /techtrends

COPY ./techtrends/requirements.txt .

RUN pip install -r requirements.txt

COPY ./techtrends .

RUN python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]