import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from config import load_from_file
from parsing import ParserService
from validation import ValidatorService
from transformation import TransformerService
from audit import AuditLogger
from common import AppError

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    parser = argparse.ArgumentParser(description="Easy SQL parser")
    parser.add_argument("--config", help="Path to custom rules.json", default=None)
    parser.add_argument("--tenant", help="Tenant ID for transformation", default="client_corp_1")
    args = parser.parse_args()

    if args.config:
        try:
            load_from_file(args.config)
            print(f"{Colors.OKBLUE}Config loaded from: {args.config}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Config load error: {e}{Colors.ENDC}")
            sys.exit(1)
    
    try:
        sql_parser = ParserService()
        validator = ValidatorService()
        transformer = TransformerService(current_tenant_id=args.tenant)
        logger = AuditLogger()
    except Exception as e:
        print(f"{Colors.FAIL}Service Init Failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    test_cases = [
        {"name": "Legitimate Select", "sql": "SELECT id, name FROM users WHERE status = 'active'"},
        {"name": "DDL Attack (DROP)", "sql": "DROP TABLE users;"},
        {"name": "Forbidden Function", "sql": "SELECT pg_sleep(5);"},
        {"name": "Select Needs Filter", "sql": "SELECT * FROM orders"},
    ]

    for _, case in enumerate(test_cases, 1):
        raw_sql = case['sql']
        print(f"Input: {raw_sql}")
        
        transformed_sql = None
        validation_res = None
        parsed = None

        try:
            parsed = sql_parser.parse(raw_sql)
            print(f"{Colors.OKBLUE}Tables: {parsed.structure.tables}, Funcs: {parsed.structure.functions}{Colors.ENDC}")

            validation_res = validator.validate(parsed)
            
            if not validation_res.is_valid:
                print(f"{Colors.FAIL}BLOCKED: {validation_res.errors}{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}ALLOWED{Colors.ENDC}")

                try:
                    transformed = transformer.transform(parsed)
                    if transformed.new_sql != raw_sql:
                        print(f"{Colors.WARNING}MODIFIED SQL:{Colors.ENDC} {transformed.new_sql}")
                        transformed_sql = transformed.new_sql
                    else:
                        print(f"{Colors.OKBLUE}No changes needed.")
                except Exception as t_err:
                    print(f"{Colors.FAIL}Transformation Error: {t_err}{Colors.ENDC}")

        except AppError as e:
            print(f"{Colors.FAIL}Logic Error: {e}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}System Error: {e}{Colors.ENDC}")
        
        if parsed and validation_res:
            logger.log(parsed, validation_res, transformed_sql)
            print(f"{Colors.OKBLUE}Logged{Colors.ENDC}")

        print(f"")

if __name__ == "__main__":
    main()