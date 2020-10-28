# set base image (host OS)
FROM python:3.6-buster

WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# add app
COPY ./gunicorn.config.py /usr/src/app
COPY ./main.py /usr/src/app
#COPY ./parser.py /usr/src/app

# command to run on container start
CMD ["gunicorn", "main:main", "-c", "gunicorn.confug.py"]