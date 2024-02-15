FROM python:3.8-bullseye
ADD dev-requirements.txt .
RUN pip install -r dev-requirements.txt

COPY kaleidoscope .
# research dev contianers to avoid pip installation^^^
WORKDIR kaleidoscope

CMD python manage.py runserver 0.0.0.0
