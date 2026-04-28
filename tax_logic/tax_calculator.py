"""부가가치세 및 종합소득세 계산."""

from .constants import (
    GENERAL_VAT_THRESHOLD,
    INCOME_TAX_BRACKETS,
    LOCAL_INCOME_TAX_RATE,
    PENALTY_LATE_PAYMENT_DAILY,
    PENALTY_NO_FILING,
    PENALTY_NO_REGISTRATION,
    SIMPLE_EXPENSE_RATE,
    SIMPLE_EXPENSE_THRESHOLD,
    SIMPLE_VAT_EXEMPT_THRESHOLD,
    SIMPLE_VAT_VALUE_ADDED_RATE,
    STANDARD_EXPENSE_RATE,
    VAT_STANDARD_RATE,
)


def classify_vat_status(annual_revenue: float, is_registered: bool) -> str:
    if not is_registered:
        return "unregistered"
    if annual_revenue < SIMPLE_VAT_EXEMPT_THRESHOLD:
        return "simple_exempt"
    if annual_revenue < GENERAL_VAT_THRESHOLD:
        return "simple_taxable"
    return "general"


def calculate_vat(annual_revenue: float, input_vat: float = 0.0, is_registered: bool = True) -> dict:
    status = classify_vat_status(annual_revenue, is_registered)

    if status in ("unregistered", "simple_exempt"):
        return {"status": status, "output_vat": 0.0, "input_vat": 0.0, "payable_vat": 0.0}

    if status == "simple_taxable":
        output_vat = annual_revenue * SIMPLE_VAT_VALUE_ADDED_RATE * VAT_STANDARD_RATE
        payable_vat = max(0.0, output_vat - input_vat)
        return {
            "status": status, "output_vat": output_vat,
            "input_vat": input_vat, "payable_vat": payable_vat,
        }

    output_vat = annual_revenue * VAT_STANDARD_RATE
    payable_vat = max(0.0, output_vat - input_vat)
    return {
        "status": status, "output_vat": output_vat,
        "input_vat": input_vat, "payable_vat": payable_vat,
    }


def apply_progressive_tax(taxable_income: float) -> float:
    if taxable_income <= 0:
        return 0.0
    for upper, rate, deduction in INCOME_TAX_BRACKETS:
        if upper is None or taxable_income <= upper:
            return taxable_income * rate - deduction
    return 0.0


def calculate_income_tax_simple_expense(annual_revenue: float) -> dict:
    applicable = annual_revenue < SIMPLE_EXPENSE_THRESHOLD
    expense = annual_revenue * SIMPLE_EXPENSE_RATE
    taxable_income = max(0.0, annual_revenue - expense)
    income_tax = apply_progressive_tax(taxable_income)
    local_tax = income_tax * LOCAL_INCOME_TAX_RATE
    return {
        "scenario": "simple_expense", "applicable": applicable,
        "expense_rate": SIMPLE_EXPENSE_RATE, "expense": expense,
        "taxable_income": taxable_income, "income_tax": income_tax,
        "local_tax": local_tax, "total_tax": income_tax + local_tax,
    }


def calculate_income_tax_standard_expense(annual_revenue: float) -> dict:
    expense = annual_revenue * STANDARD_EXPENSE_RATE
    taxable_income = max(0.0, annual_revenue - expense)
    income_tax = apply_progressive_tax(taxable_income)
    local_tax = income_tax * LOCAL_INCOME_TAX_RATE
    return {
        "scenario": "standard_expense", "applicable": True,
        "expense_rate": STANDARD_EXPENSE_RATE, "expense": expense,
        "taxable_income": taxable_income, "income_tax": income_tax,
        "local_tax": local_tax, "total_tax": income_tax + local_tax,
    }


def calculate_income_tax_actual_expense(annual_revenue: float, actual_expense: float) -> dict:
    taxable_income = max(0.0, annual_revenue - actual_expense)
    income_tax = apply_progressive_tax(taxable_income)
    local_tax = income_tax * LOCAL_INCOME_TAX_RATE
    return {
        "scenario": "actual_expense", "applicable": True,
        "expense_rate": None, "expense": actual_expense,
        "taxable_income": taxable_income, "income_tax": income_tax,
        "local_tax": local_tax, "total_tax": income_tax + local_tax,
    }


def calculate_all_scenarios(annual_revenue: float, actual_expense: float = 0.0) -> list:
    return [
        calculate_income_tax_simple_expense(annual_revenue),
        calculate_income_tax_standard_expense(annual_revenue),
        calculate_income_tax_actual_expense(annual_revenue, actual_expense),
    ]


def calculate_penalties(payable_tax: float, annual_revenue: float = 0.0,
                        is_unregistered: bool = False, days_late: int = 0) -> dict:
    no_filing = payable_tax * PENALTY_NO_FILING
    no_registration = annual_revenue * PENALTY_NO_REGISTRATION if is_unregistered else 0.0
    late_payment = payable_tax * PENALTY_LATE_PAYMENT_DAILY * max(0, days_late)
    return {
        "no_filing": no_filing,
        "no_registration": no_registration,
        "late_payment": late_payment,
        "total_penalty": no_filing + no_registration + late_payment,
    }
