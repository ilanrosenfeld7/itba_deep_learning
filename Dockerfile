FROM python:3.9
WORKDIR /recommendations_api
COPY . /recommendations_api
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "recommendations_api.py"]