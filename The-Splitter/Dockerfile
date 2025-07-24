FROM alpine:3.20
RUN apk add --no-cache python3 py3-pip
RUN apk add ffmpeg
WORKDIR /home/splitter
COPY ./api.py .
COPY ./requirements.txt .
COPY ./setup.py .
COPY ./splitter.py .
COPY ./README.md .
COPY ./templates ./templates
COPY ./static ./static
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN venv/bin/pip install build
RUN venv/bin/pip install .
EXPOSE 5000
ENTRYPOINT ["venv/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "300", "api:app"]
