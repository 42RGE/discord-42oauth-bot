FROM python:3.11-slim as build

RUN apt-get update && apt-get install -y \
    curl \
    wget

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0", "--port=4242"]
