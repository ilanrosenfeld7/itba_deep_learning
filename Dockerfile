FROM python:3.9
WORKDIR /recommendations_api
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT python recommendations_api.py