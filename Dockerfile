FROM python:3.12-slim

WORKDIR /scoring-engine

COPY app/ ./app/

ENV PYTHONUNBUFFERED=1
ENV SCORING_INPUT_FILE=/scoring-engine/data/customers.csv
ENV SCORING_OUTPUT_FILE=/scoring-engine/output/scoring_results.csv

CMD ["python", "app/scoring_engine.py"]
