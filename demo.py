import sys

sys.path.append('src')

try:
    from parsing import ParserService
    from validation import ValidatorService
    from transformation import TransformerService
    from common.errors import AppError, ParsingError
    from common.models import *
except ImportError as e:
    print(f"Ошибка импорта. Убедитесь, что все файлы созданы в src/...")
    print(f"Детали: {e}")
    sys.exit(1)

parser = ParserService()
validator = ValidatorService()
transformer = TransformerService(tenant_id='my-tenant-123') 

queries_to_test = [
    "SELECT name FROM users",
    "SELECT * FROM orders WHERE amount > 100",
    "DROP TABLE users",
    "INSERT INTO logs (data) VALUES ('test')",
    "SELECT * FROM users u JOIN secrets s ON u.id = s.user_id"
]

print("--- SQL Analyzer Pipeline ---")

for sql in queries_to_test:
    print(f"\nProcessing: '{sql}'")
    try:
        parsed_query = parser.parse(sql)
        
        validation_result = validator.validate(parsed_query)
        
        if not validation_result.is_valid:
            print(f"  Result: ❌ INVALID")
            for err in validation_result.errors:
                print(f"    -> {err}")
            continue

        print("  Result: ✅ VALID")

        transformed_query = transformer.add_tenant_security(parsed_query)
        
        if transformed_query.new_sql != sql:
            print(f"  Transformed: '{transformed_query.new_sql}'")
        else:
            print("  (No transformation applied)")
            
    except ParsingError as e:
        print(f"  Result: ❌ PARSE FAILED: {e}")
    except AppError as e:
        print(f"  Pipeline Error: {e}")
    except Exception as e:
        print(f"  UNEXPECTED ERROR: {e}")