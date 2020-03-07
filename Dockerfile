FROM python:3.7.4-stretch AS builder

RUN mkdir -p /backend
ADD app.py /backend/
ADD requirements.txt /backend/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /backend/requirements.txt

RUN mkdir -p /data
ADD /data /data/

EXPOSE 8844
CMD ["gunicorn", "-w 1", "-b 0.0.0.0:8844", "backend.app:app"]