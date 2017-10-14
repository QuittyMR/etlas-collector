#!/bin/bash
set -e

source build/bin/activate
rq worker account_schedules --name sanjer1 --verbose --url redis://localhost/7 --path <application folder>/scraper-collector/app --results-ttl 1209600