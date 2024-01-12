FROM python:3.11-alpine3.19

ENV PYTHONUNBUFFERED 1

RUN pip install gunicorn
RUN mkdir /app
ADD . /app/
WORKDIR /app
RUN chmod +x entry_point.sh

RUN pip install -r requirements.txt

ENTRYPOINT [ "./entry_point.sh" ]
