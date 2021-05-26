#!/bin/bash

while true; do
    flask db init
    flask db migrate
    flask db upgrade
    if [[ "$?" == "0" ]]; then
      break
    fi
    echo retrying in 5 secs...
    sleep 5
done

exec gunicorn -b 0.0.0.0:8000 FLChat:app

