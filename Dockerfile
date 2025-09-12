FROM nginx:stable-alpine
RUN apk add --no-cache python3 py3-pip
RUN apk add ffmpeg
WORKDIR /app

# Copy project files
COPY ffcuesplitter-rest-api/*.py ./
COPY ffcuesplitter-rest-api/templates ./templates
COPY ffcuesplitter-rest-api/static ./static
COPY ffcuesplitter-rest-api/requirements.txt ./

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

