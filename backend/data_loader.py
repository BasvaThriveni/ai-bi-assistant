import csv
import json
from datetime import datetime
from pathlib import Path

from backend.database import init_db, insert_validation_issue, reset_import_state, save_import_summary, upsert_transaction

BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_CSV_PATH = Path('/home/user/RSG/JD and Assessment for GETs/ai_bi_assistant_sales_data - GET.csv')
PROJECT_CSV_PATH = BASE_DIR / 'data' / 'sales_data.csv'

REQUIRED_COLUMNS = [
    'Transaction_Id',
    'Order_date',
    'Product',
    'Category',
    'Region',
    'Sales_channel',
    'Quantity',
    'Unit_price',
    'Discount_amount',
    'Status',
]


def copy_csv_if_needed() -> Path:
    PROJECT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not PROJECT_CSV_PATH.exists():
        PROJECT_CSV_PATH.write_bytes(SOURCE_CSV_PATH.read_bytes())
    return PROJECT_CSV_PATH


def parse_date(value: str) -> str:
    date_value = (value or '').strip()
    if not date_value:
        raise ValueError('Missing date value')
    dt = datetime.strptime(date_value, '%d-%m-%Y')
    return dt.strftime('%Y-%m-%d')


def clean_numeric(value: str | None, field_name: str) -> float | None:
    if value is None or str(value).strip() == '':
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        raise ValueError(f'Invalid numeric value for {field_name}: {value}')


def validate_and_prepare_row(raw_row: dict) -> dict:
    row = {k: (v.strip() if isinstance(v, str) else v) for k, v in raw_row.items()}
    transaction_id = (row.get('Transaction_Id') or '').strip()
    status = (row.get('Status') or '').strip()
    product = (row.get('Product') or '').strip()
    category = (row.get('Category') or '').strip()
    region = (row.get('Region') or '').strip()
    sales_channel = (row.get('Sales_channel') or '').strip()

    issues = []
    if not transaction_id:
        issues.append(('missing_transaction_id', 'Transaction ID is missing', 'error'))
    if not product:
        issues.append(('missing_product', 'Product is missing', 'error'))
    if not category:
        issues.append(('missing_category', 'Category is missing', 'error'))
    if not region:
        issues.append(('missing_region', 'Region is missing', 'error'))
    if not sales_channel:
        issues.append(('missing_sales_channel', 'Sales channel is missing', 'error'))

    order_date = row.get('Order_date')
    try:
        normalized_date = parse_date(order_date)
    except ValueError:
        normalized_date = ''
        issues.append(('invalid_date', f'Invalid order date: {order_date}', 'error'))

    try:
        quantity = int(float(str(row.get('Quantity', '')).strip()))
        if quantity is None:
            raise ValueError('Missing quantity')
    except (TypeError, ValueError):
        quantity = None
        issues.append(('invalid_quantity', f'Invalid quantity: {row.get("Quantity")}', 'error'))

    try:
        unit_price_raw = clean_numeric(row.get('Unit_price'), 'Unit_price')
        if unit_price_raw is None:
            raise ValueError('Missing unit price')
    except ValueError as exc:
        unit_price_raw = None
        issues.append(('missing_or_invalid_unit_price', str(exc), 'error'))

    try:
        discount_amount = clean_numeric(row.get('Discount_amount'), 'Discount_amount') or 0.0
    except ValueError as exc:
        discount_amount = 0.0
        issues.append(('invalid_discount_amount', str(exc), 'error'))

    is_eligible = True
    exclusion_reason = None

    if status.lower() == 'returned':
        is_eligible = False
        exclusion_reason = 'Returned order excluded from completed-sales revenue.'
        issues.append(('returned_transaction', f'Transaction {transaction_id} has Returned status.', 'warning'))
    if quantity is None:
        is_eligible = False
        exclusion_reason = exclusion_reason or 'Invalid or missing quantity.'
    elif quantity == 0:
        is_eligible = False
        exclusion_reason = exclusion_reason or 'Zero quantity excluded from revenue.'
        issues.append(('zero_quantity', f'Transaction {transaction_id} has zero quantity.', 'warning'))
    if unit_price_raw is None:
        is_eligible = False
        exclusion_reason = exclusion_reason or 'Missing or invalid unit price.'
    elif unit_price_raw <= 0:
        is_eligible = False
        exclusion_reason = exclusion_reason or 'Unit price must be greater than zero.'

    prepared = {
        'transaction_id': transaction_id,
        'order_date': normalized_date,
        'product': product,
        'category': category,
        'region': region,
        'sales_channel': sales_channel,
        'quantity': quantity,
        'unit_price': unit_price_raw,
        'discount_amount': discount_amount,
        'status': status,
        'is_eligible_for_revenue': 1 if is_eligible else 0,
        'exclusion_reason': exclusion_reason,
        'raw_row_json': json.dumps(row, ensure_ascii=True),
    }

    for issue_code, detail, severity in issues:
        insert_validation_issue(transaction_id if transaction_id else None, issue_code, detail, severity)

    return prepared


def import_sales_csv(csv_path: str | Path | None = None) -> dict:
    init_db()
    reset_import_state()
    source_path = Path(csv_path) if csv_path else copy_csv_if_needed()
    total_rows = 0
    imported_records = 0
    accepted_for_revenue = 0
    excluded_for_revenue = 0
    duplicate_rows = 0

    with open(source_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        actual_headers = reader.fieldnames or []
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in actual_headers]
        if missing_columns:
            raise ValueError(f'Missing required columns: {missing_columns}')

        for row in reader:
            total_rows += 1
            prepared = validate_and_prepare_row(row)

            if not prepared['transaction_id']:
                continue

            if prepared['status'].lower() == 'returned':
                upsert_transaction(prepared)
                imported_records += 1
                excluded_for_revenue += 1
                continue

            if prepared['quantity'] is None or prepared['quantity'] == 0 or prepared['unit_price'] is None or prepared['unit_price'] <= 0:
                upsert_transaction(prepared)
                imported_records += 1
                excluded_for_revenue += 1
                continue

            if prepared['status'] == 'Completed':
                accepted_for_revenue += 1

            upsert_transaction(prepared)
            imported_records += 1

    if total_rows == 0:
        raise ValueError('No rows found in source CSV.')

    save_import_summary(
        source_file=str(source_path),
        total_rows=total_rows,
        imported_records=imported_records,
        accepted_for_revenue=accepted_for_revenue,
        excluded_for_revenue=excluded_for_revenue,
        duplicate_rows=duplicate_rows,
        notes='Original records preserved; excluded records tracked with validation issues.',
    )

    return {
        'total_rows': total_rows,
        'imported_records': imported_records,
        'accepted_for_revenue': accepted_for_revenue,
        'excluded_for_revenue': excluded_for_revenue,
        'duplicate_rows': duplicate_rows,
        'source_path': str(source_path),
    }


if __name__ == '__main__':
    summary = import_sales_csv()
    print(json.dumps(summary, indent=2))
