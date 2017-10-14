#!/bin/bash
set -e
APP_VERSION=$1

echo -ne "\n\nContainerizing...\n\n"
docker build -t scraper-collector:${APP_VERSION} .
echo -ne "\n\nDone!\n\n"
