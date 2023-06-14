FROM python:3.9-slim
COPY requirements.txt .
# RUN apk --no-cache add musl-dev linux-headers g++
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
