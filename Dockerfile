FROM python:3.6-slim

COPY ./service /service
WORKDIR /service

RUN pip install -r requirements.txt

EXPOSE 5000/tcp

ENTRYPOINT ["python3"]
CMD ["youtrack-service.py"]


