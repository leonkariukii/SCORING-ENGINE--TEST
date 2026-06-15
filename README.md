# Automated Loan Scoring Engine

This project runs the loan scoring engine inside Docker, which makes it easier to use from Ubuntu/WSL or a server environment.

## Files

- `data/customers.csv` - applicant input file
- `output/scoring_results.csv` - generated scoring results
- `app/scoring_engine.py` - scoring logic
- `samples/sample_bank_statement.pdf` - fictional bank statement for PDF upload testing
- `uploads/` - place bank statement PDFs here before processing
- `Dockerfile` - container definition
- `docker-compose.yml` - simple container runner

## Run With Docker Compose

```bash
docker compose up --build
```

On Windows PowerShell, you can also run:

```powershell
.\run-docker.ps1
```

## Run With Plain Docker

```bash
docker build -t scoring-engine .
docker run --rm \
  -v "$PWD/data:/scoring-engine/data" \
  -v "$PWD/output:/scoring-engine/output" \
  scoring-engine
```

## Run From WSL Ubuntu

If Ubuntu is not installed yet:

```powershell
wsl --install -d Ubuntu
```

Restart the machine if Windows asks you to, then open Ubuntu and run:

```bash
cd /mnt/c/Users/USER/Documents/Scoring\ Engine
docker compose up --build
```

If Docker says it cannot connect to the Docker API, start Docker Desktop and make sure WSL integration is enabled for Ubuntu.

After running, open:

```text
output/scoring_results.csv
```

## Output Analysis

The results include:

- final score
- risk band
- approval decision
- debt-to-income percentage
- disposable income after debt payments
- scoring reasons and automatic rejection reasons

## PDF Statement Testing

A fictional sample bank statement is included here:

```text
samples/sample_bank_statement.pdf
```

To test the upload flow manually for now, copy a PDF into:

```text
uploads/
```

For the next phase, this PDF can be used as the upload test file. The practical flow will be:

1. Upload a customer bank statement PDF.
2. Extract statement details such as income deposits, loan repayments, total debits, total credits, average balance, and closing balance.
3. Convert those extracted values into scoring inputs.
4. Run the scoring engine.
5. Save both the extracted financial analysis and the final credit decision.
