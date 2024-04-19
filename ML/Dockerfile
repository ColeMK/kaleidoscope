#Dockerfile for ML Container

FROM python:3.10

ADD ml_requirements.txt .
RUN pip install -r ml_requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
#Hopefully this will copy the whole directory
COPY . /ML
WORKDIR /ML

#Add command later

CMD ["python3", "db_stream.py"]