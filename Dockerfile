FROM ubuntu:focal

RUN apt-get update -y && \
  apt-get install -qqy python3 python3-pip python3-dev libmariadb-dev curl

EXPOSE 8000
WORKDIR /var/www/saus
ADD . /var/www/saus

RUN pip3 install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8000", "saus.wsgi:application"]
