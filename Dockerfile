# set base image (host OS)
FROM python:3.9-buster

WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add app
COPY ./gunicorn.config.py /usr/src/app/gunicorn.config.py
COPY ./main.py /usr/src/app/main.py
COPY ./parser.py /usr/src/app/parser.py

# command to run on container start
CMD ["gunicorn", "main:main", "-c", "gunicorn.config.py"]
