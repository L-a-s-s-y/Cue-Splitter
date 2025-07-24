#!/bin/bash

cd The-Splitter
docker build -t cue-splitter/splitter .
cd ../Reverse-proxy
docker build -t cue-splitter/proxy .
cd ..
docker compose up -d
