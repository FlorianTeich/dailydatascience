# daily data science

Trying to do some data science one day at a time

## Setup

Clone the repo and install all dependencies via uv

## Activate the connector:

curl -X POST -H "Content-Type: application/json" \
  --data @connectors/postgres-connector.json \
  http://localhost:8083/connectors