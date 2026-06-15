import csv
import os
from pathlib import Path


BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
INPUT_FILE = Path(os.getenv("SCORING_INPUT_FILE", PROJECT_DIR / "data" / "customers.csv"))
OUTPUT_FILE = Path(os.getenv("SCORING_OUTPUT_FILE", PROJECT_DIR / "output" / "scoring_results.csv"))


CSV_FIELDS = [
    "customer_id",
    "name",
    "age",
    "monthly_income",
    "employment_years",
    "existing_loans",
    "monthly_debt_payments",
    "credit_history_years",
    "missed_payments_last_12_months"
]


NUMERIC_FIELDS = {
    "age": int,
    "monthly_income": float,
    "employment_years": float,
    "existing_loans": int,
    "monthly_debt_payments": float,
    "credit_history_years": float,
    "missed_payments_last_12_months": int
}


REQUIRED_FIELDS = {
    "customer_id": str,
    "name": str,
    "age": int,
    "monthly_income": (int, float),
    "employment_years": (int, float),
    "existing_loans": int,
    "monthly_debt_payments": (int, float),
    "credit_history_years": (int, float),
    "missed_payments_last_12_months": int
}


SAMPLE_CUSTOMERS = [
    {
        "customer_id": "CUST-001",
        "name": "Amina Otieno",
        "age": 30,
        "monthly_income": 80000,
        "employment_years": 4,
        "existing_loans": 1,
        "monthly_debt_payments": 12000,
        "credit_history_years": 5,
        "missed_payments_last_12_months": 0
    },
    {
        "customer_id": "CUST-002",
        "name": "Brian Kariuki",
        "age": 23,
        "monthly_income": 42000,
        "employment_years": 1,
        "existing_loans": 2,
        "monthly_debt_payments": 18000,
        "credit_history_years": 1,
        "missed_payments_last_12_months": 2
    },
    {
        "customer_id": "CUST-003",
        "name": "Grace Wanjiku",
        "age": 41,
        "monthly_income": 150000,
        "employment_years": 9,
        "existing_loans": 0,
        "monthly_debt_payments": 0,
        "credit_history_years": 8,
        "missed_payments_last_12_months": 0
    }
]


def create_sample_input_file():
    if INPUT_FILE.exists():
        return

    INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(SAMPLE_CUSTOMERS)

    print(f"Created sample input file: {INPUT_FILE}")


def load_customers_from_csv():
    customers = []

    with INPUT_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            customers.append(clean_csv_row(row, row_number))

    return customers


def clean_csv_row(row, row_number):
    customer = {}
    parse_errors = []

    for field in CSV_FIELDS:
        value = row.get(field, "")

        if isinstance(value, str):
            value = value.strip()

        if field in NUMERIC_FIELDS and value != "":
            try:
                value = NUMERIC_FIELDS[field](value)
            except ValueError:
                parse_errors.append(f"Row {row_number}: {field} must be numeric")

        customer[field] = value

    customer["_parse_errors"] = parse_errors
    return customer


def validate_customer(customer):
    errors = list(customer.get("_parse_errors", []))

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in customer or customer[field] == "":
            errors.append(f"Missing required field: {field}")
        elif not isinstance(customer[field], expected_type):
            errors.append(f"{field} must be a valid {format_expected_type(expected_type)}")

    if errors:
        return errors

    if not customer["customer_id"].strip():
        errors.append("customer_id cannot be blank")

    if not customer["name"].strip():
        errors.append("name cannot be blank")

    if customer["age"] < 18 or customer["age"] > 100:
        errors.append("age must be between 18 and 100")

    if customer["monthly_income"] <= 0:
        errors.append("monthly_income must be greater than 0")

    if customer["employment_years"] < 0:
        errors.append("employment_years cannot be negative")

    if customer["existing_loans"] < 0:
        errors.append("existing_loans cannot be negative")

    if customer["monthly_debt_payments"] < 0:
        errors.append("monthly_debt_payments cannot be negative")

    if customer["monthly_debt_payments"] > customer["monthly_income"]:
        errors.append("monthly_debt_payments cannot be greater than monthly_income")

    if customer["credit_history_years"] < 0:
        errors.append("credit_history_years cannot be negative")

    if customer["missed_payments_last_12_months"] < 0:
        errors.append("missed_payments_last_12_months cannot be negative")

    return errors


def format_expected_type(expected_type):
    if isinstance(expected_type, tuple):
        return " or ".join(value.__name__ for value in expected_type)

    return expected_type.__name__


def calculate_score(customer):
    score = 0
    reasons = []

    income_score, income_reason = score_income(customer["monthly_income"])
    score += income_score
    reasons.append(income_reason)

    employment_score, employment_reason = score_employment(customer["employment_years"])
    score += employment_score
    reasons.append(employment_reason)

    debt_score, debt_reason = score_debt_burden(
        customer["monthly_income"],
        customer["monthly_debt_payments"]
    )
    score += debt_score
    reasons.append(debt_reason)

    credit_score, credit_reason = score_credit_history(customer["credit_history_years"])
    score += credit_score
    reasons.append(credit_reason)

    repayment_score, repayment_reason = score_repayment_behavior(
        customer["missed_payments_last_12_months"]
    )
    score += repayment_score
    reasons.append(repayment_reason)

    loan_score, loan_reason = score_existing_loans(customer["existing_loans"])
    score += loan_score
    reasons.append(loan_reason)

    age_score, age_reason = score_age(customer["age"])
    score += age_score
    reasons.append(age_reason)

    return score, reasons


def calculate_financial_metrics(customer):
    debt_to_income_ratio = customer["monthly_debt_payments"] / customer["monthly_income"]
    monthly_disposable_income = customer["monthly_income"] - customer["monthly_debt_payments"]

    return {
        "debt_to_income_percent": round(debt_to_income_ratio * 100, 1),
        "monthly_disposable_income": round(monthly_disposable_income, 2)
    }


def score_income(monthly_income):
    if monthly_income >= 150000:
        return 20, "Income is very strong: +20"
    if monthly_income >= 80000:
        return 16, "Income is strong: +16"
    if monthly_income >= 50000:
        return 12, "Income is acceptable: +12"
    if monthly_income >= 30000:
        return 6, "Income is modest: +6"

    return 0, "Income is below the preferred minimum: +0"


def score_employment(employment_years):
    if employment_years >= 5:
        return 15, "Employment history is stable: +15"
    if employment_years >= 2:
        return 10, "Employment history is acceptable: +10"
    if employment_years >= 1:
        return 5, "Employment history is short: +5"

    return 0, "Employment history is too limited: +0"


def score_debt_burden(monthly_income, monthly_debt_payments):
    debt_to_income_ratio = monthly_debt_payments / monthly_income
    percentage = round(debt_to_income_ratio * 100, 1)

    if debt_to_income_ratio <= 0.20:
        return 20, f"Debt burden is low at {percentage}% of income: +20"
    if debt_to_income_ratio <= 0.35:
        return 14, f"Debt burden is manageable at {percentage}% of income: +14"
    if debt_to_income_ratio <= 0.50:
        return 7, f"Debt burden is high at {percentage}% of income: +7"

    return 0, f"Debt burden is very high at {percentage}% of income: +0"


def score_credit_history(credit_history_years):
    if credit_history_years >= 5:
        return 15, "Credit history is well established: +15"
    if credit_history_years >= 2:
        return 10, "Credit history is moderate: +10"
    if credit_history_years >= 1:
        return 5, "Credit history is limited: +5"

    return 0, "No meaningful credit history: +0"


def score_repayment_behavior(missed_payments):
    if missed_payments == 0:
        return 15, "No missed payments in the last 12 months: +15"
    if missed_payments == 1:
        return 8, "One missed payment in the last 12 months: +8"
    if missed_payments == 2:
        return 3, "Two missed payments in the last 12 months: +3"

    return 0, "Several missed payments in the last 12 months: +0"


def score_existing_loans(existing_loans):
    if existing_loans == 0:
        return 10, "No existing loans: +10"
    if existing_loans == 1:
        return 7, "One existing loan: +7"
    if existing_loans == 2:
        return 3, "Two existing loans: +3"

    return 0, "Too many existing loans: +0"


def score_age(age):
    if 25 <= age <= 60:
        return 5, "Age is within the preferred lending range: +5"
    if 21 <= age < 25 or 60 < age <= 70:
        return 2, "Age is acceptable but outside the preferred range: +2"

    return 0, "Age is higher risk for this scoring model: +0"


def get_automatic_rejection_reasons(customer):
    reasons = []
    debt_to_income_ratio = customer["monthly_debt_payments"] / customer["monthly_income"]

    if customer["missed_payments_last_12_months"] >= 4:
        reasons.append("4 or more missed payments in the last 12 months")

    if debt_to_income_ratio > 0.65:
        reasons.append("Debt payments are above 65% of monthly income")

    if customer["existing_loans"] >= 5:
        reasons.append("5 or more existing loans")

    if customer["monthly_income"] < 20000:
        reasons.append("Monthly income is below the minimum lending threshold")

    return reasons


def get_risk_band(score):
    if score >= 80:
        return "LOW RISK"
    if score >= 60:
        return "MEDIUM RISK"

    return "HIGH RISK"


def make_decision(score, automatic_rejection_reasons):
    if automatic_rejection_reasons:
        return "REJECTED"
    if score >= 80:
        return "APPROVED"
    if score >= 60:
        return "REVIEW"

    return "REJECTED"


def process_application(customer):
    validation_errors = validate_customer(customer)

    if validation_errors:
        return {
            "customer_id": customer.get("customer_id", "UNKNOWN"),
            "name": customer.get("name", "UNKNOWN"),
            "status": "ERROR",
            "score": "",
            "risk_band": "",
            "decision": "ERROR",
            "reasons": validation_errors
        }

    score, reasons = calculate_score(customer)
    financial_metrics = calculate_financial_metrics(customer)
    automatic_rejection_reasons = get_automatic_rejection_reasons(customer)
    risk_band = get_risk_band(score)
    decision = make_decision(score, automatic_rejection_reasons)

    for reason in automatic_rejection_reasons:
        reasons.append(f"Automatic rejection: {reason}")

    return {
        "customer_id": customer["customer_id"],
        "name": customer["name"],
        "status": "OK",
        "score": score,
        "risk_band": risk_band,
        "decision": decision,
        "debt_to_income_percent": financial_metrics["debt_to_income_percent"],
        "monthly_disposable_income": financial_metrics["monthly_disposable_income"],
        "reasons": reasons
    }


def process_applications(customers):
    results = []

    for customer in customers:
        results.append(process_application(customer))

    return results


def save_results_to_csv(results):
    fieldnames = [
        "customer_id",
        "name",
        "status",
        "score",
        "risk_band",
        "decision",
        "debt_to_income_percent",
        "monthly_disposable_income",
        "reasons"
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = result.copy()
            row["reasons"] = " | ".join(result["reasons"])
            writer.writerow(row)


def print_results(results):
    for result in results:
        print("-" * 60)
        print(f"Customer: {result['name']} ({result['customer_id']})")

        if result["status"] == "ERROR":
            print("Status: ERROR")
            print("Validation issues:")
            for error in result["reasons"]:
                print(f"- {error}")
            continue

        print(f"Score: {result['score']}/100")
        print(f"Risk band: {result['risk_band']}")
        print(f"Decision: {result['decision']}")
        print(f"Debt-to-income: {result['debt_to_income_percent']}%")
        print(f"Disposable income after debt: {result['monthly_disposable_income']}")
        print("Scoring reasons:")
        for reason in result["reasons"]:
            print(f"- {reason}")


def main():
    create_sample_input_file()
    customers = load_customers_from_csv()
    results = process_applications(customers)
    save_results_to_csv(results)
    print_results(results)
    print("-" * 60)
    print(f"Results saved to: {OUTPUT_FILE}")


main()
