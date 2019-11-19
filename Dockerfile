FROM python:3.7.1-stretch

RUN mkdir -p /backend
RUN mkdir -p /data
ADD /data /data/
ADD app.py /backend/
ADD requirements.txt /backend/

RUN pip install --no-cache-dir -r /backend/requirements.txt
