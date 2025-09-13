FROM nginx:stable-alpine
RUN apk add --no-cache python3 py3-pip
RUN apk add ffmpeg
WORKDIR /app

# Copy project files
COPY cue-splitter/*.py ./
COPY cue-splitter/templates ./templates
COPY cue-splitter/static ./static
COPY cue-splitter/requirements.txt ./

# Create venv
RUN python3 -m venv venv
    
# Install requirements and project
RUN source venv/bin/activate && \
    pip install -r requirements.txt && \
    pip install .

# Copy entrypoint and config files    
COPY docker/entrypoint.sh /
COPY docker/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 5000
CMD ["/entrypoint.sh"]

