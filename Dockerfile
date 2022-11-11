FROM python:3.8-slim-buster
COPY ./service /service
WORKDIR /service
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3","-u","youtrack-service.py"]



