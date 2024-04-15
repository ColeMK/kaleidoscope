# FROM python:3.8-bullseye
# ADD dev-requirements.txt .
# RUN pip install -r dev-requirements.txt

# COPY kaleidoscope .
# # research dev contianers to avoid pip installation^^^
# WORKDIR kaleidoscope

# CMD python manage.py runserver 0.0.0.0


# Coles Changes

FROM python:3.10

#Dont really know what this is but needed for network communication
ENV PYTHONUNBUFFERED 1 
WORKDIR /app
COPY webserver-requirements.txt /app/
RUN pip install -r webserver-requirements.txt

COPY . /app/


#EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:80"] 

#keep
