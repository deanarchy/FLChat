FROM python:3.6

WORKDIR /flchat

ENV FLASK_APP FLChat.py

COPY Pipfile Pipfile.lock /flchat/
RUN pip install pipenv && pipenv install --system

COPY app app
COPY FLChat.py config.py boot.sh ./

RUN chmod +x boot.sh
ENTRYPOINT ["./boot.sh"]