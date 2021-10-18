FROM python:3.8.9-slim
# ENV PYTHONUNBUFFERED=1
WORKDIR /myproject

RUN pip install discord.py==1.7.3
RUN pip install python-dotenv==0.19.1

RUN mkdir ./db
COPY . .
CMD ["python", "client.py"]

# docker build . -t temp-discord
# docker run --rm -t temp-discord