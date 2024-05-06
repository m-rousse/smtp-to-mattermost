FROM python:alpine3.18
WORKDIR /app
ENV PYTHONPATH /app
ADD ./requirements.txt /app/requirements.txt
RUN apk add --no-cache git && pip install -r requirements.txt
ADD ./ /app
RUN mkdir -p /etc/smtp-to-mattermost
CMD ["aiosmtpd", "-n", "-l", "0.0.0.0:8025", "-c", "handler.MessageHandler"]
EXPOSE 8025
