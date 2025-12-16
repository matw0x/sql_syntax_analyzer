import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from parsing import ParserService
from validation import ValidatorService
from transformation import TransformerService
from audit import AuditLogger
from common import AppError

def main():
    try:
        base_dir = Path(__file__).resolve().parent
        log_path = base_dir / "artifacts" / "audit.jsonl"

        parser = ParserService()
        validator = ValidatorService()
        transformer = TransformerService(current_tenant_id="db_integration_user")
        logger = AuditLogger(log_file=str(log_path))
    except Exception as e:
        sys.stderr.write(f"Init failed: {e}\n")
        sys.exit(1)

    for line in sys.stdin:
        raw_sql = line.strip()
        if not raw_sql:
            continue

        try:
            parsed = parser.parse(raw_sql)
            validation_res = validator.validate(parsed)
            
            transformed_sql = None
            if validation_res.is_valid:
                try:
                    t_res = transformer.transform(parsed)
                    if t_res.new_sql != raw_sql:
                        transformed_sql = t_res.new_sql
                except Exception:
                    pass
            
            logger.log(parsed, validation_res, transformed_sql)
            
        except AppError:
            pass
        except Exception as e:
            sys.stderr.write(f"Error processing {raw_sql[:30]}...: {e}\n")

if __name__ == "__main__":
    main()