# Automated Loan Scoring Engine

This project scores loan applicants from a CSV file and writes the result to another CSV file. It can run directly with Python, but the recommended way is Docker because Docker gives the project the same environment every time.

## Project Files

- `app/scoring_engine.py` - the scoring logic
- `data/customers.csv` - the main customer input file
- `data/customers_second_sample.csv` - another sample input file for testing
- `output/scoring_results.csv` - generated result file after the engine runs
- `Dockerfile` - instructions for building the Docker image
- `docker-compose.yml` - simple Docker runner
- `samples/sample_bank_statement.pdf` - fictional PDF statement for later upload testing
- `uploads/` - folder for future uploaded PDF statements

## Run From Ubuntu/WSL

Open Ubuntu and go to the project folder:

```bash
cd "/mnt/c/Users/USER/Documents/Scoring Engine"
```

Check that the files are there:

```bash
ls
```

Run the scoring engine:

```bash
docker compose up --build
```

View the results:

```bash
cat output/scoring_results.csv
```

If Docker says it cannot connect, open Docker Desktop on Windows first, wait until Docker is running, then run the command again.

## Run With Plain Docker

```bash
docker build -t scoring-engine .

docker run --rm \
  -v "$PWD/data:/scoring-engine/data" \
  -v "$PWD/output:/scoring-engine/output" \
  scoring-engine
```

## Try The Second Sample File

The engine normally reads:

```text
data/customers.csv
```

To test the second sample file without deleting the original, run:

```bash
docker compose run --rm \
  -e SCORING_INPUT_FILE=/scoring-engine/data/customers_second_sample.csv \
  scoring-engine
```

Then view the results:

```bash
cat output/scoring_results.csv
```

## Edit Customer Data

From Ubuntu:

```bash
nano data/customers.csv
```

Save in nano:

```text
Ctrl + O
Enter
Ctrl + X
```

Or open the folder in Windows File Explorer:

```bash
explorer.exe .
```

Then edit `data/customers.csv` with Notepad or VS Code.

## Upload Changes To GitHub

After changing files, run:

```bash
git status
git add .
git commit -m "Describe what changed"
git push
```

Example:

```bash
git add .
git commit -m "Improve Docker instructions"
git push
```

## Run More Than One Engine

Copy the project folder:

```bash
cd "/mnt/c/Users/USER/Documents"
cp -r "Scoring Engine" "Scoring Engine 2"
```

Run the first engine:

```bash
cd "/mnt/c/Users/USER/Documents/Scoring Engine"
docker compose -p scoring-engine-1 up --build
```

Run the second engine in another Ubuntu window:

```bash
cd "/mnt/c/Users/USER/Documents/Scoring Engine 2"
docker compose -p scoring-engine-2 up --build
```

The `-p` value gives each Docker run its own project name.

## Output Fields

The results include:

- score
- risk band
- approval decision
- debt-to-income percentage
- monthly disposable income
- scoring reasons
- automatic rejection reasons

## Future PDF Upload Flow

The sample PDF is here:

```text
samples/sample_bank_statement.pdf
```

The future upload flow can be:

1. Upload a customer bank statement PDF.
2. Extract income deposits, loan repayments, debits, credits, and balances.
3. Convert the extracted values into scoring inputs.
4. Run the scoring engine.
5. Save the financial analysis and final credit decision.
