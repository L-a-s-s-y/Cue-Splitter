#!/bin/bash
mkdir /tmp/splitter
# Luego hay que evitar hacer esto sino hacer al usuario y grupo de docker propietario del directorio
#chmod 775 /tmp/splitter
cd The-Splitter
docker build -t cue-splitter/splitter .
cd ../Reverse-proxy
docker build -t cue-splitter/proxy .
cd ..
docker compose up -d
