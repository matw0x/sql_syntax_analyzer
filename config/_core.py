import json
from pathlib import Path
from dataclasses import dataclass

DEFAULT_CONFIG_PATH = Path(__file__).parent / "rules.json"

@dataclass
class ParsingConfig:
    known_aggregates: list[str]

@dataclass
class ValidationConfig:
    enabled: bool
    forbidden_statements: list[str]
    forbidden_functions: list[str]

@dataclass
class TenantInjectionConfig:
    enabled: bool
    target_column: str

@dataclass
class TransformationRules:
    tenant_injection: TenantInjectionConfig

@dataclass
class TransformationConfig:
    enabled: bool
    allowed_statements: list[str]
    rules: TransformationRules

class AppConfig:
    def __init__(self, path: Path | str = None):
        target_path = Path(path) if path else DEFAULT_CONFIG_PATH
        
        if not target_path.exists():
            raise FileNotFoundError(f"Config file not found: {target_path}")

        with open(target_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                
                self.parsing = ParsingConfig(**data["parsing"])
                self.validation = ValidationConfig(**data["validation"])
                
                t_data = data["transformation"]
                rules_data = t_data["rules"]
                
                tenant_conf = TenantInjectionConfig(**rules_data["tenant_injection"])
                rules_conf = TransformationRules(tenant_injection=tenant_conf)
                
                self.transformation = TransformationConfig(
                    enabled=t_data["enabled"],
                    allowed_statements=t_data["allowed_statements"],
                    rules=rules_conf
                )
                
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                raise ValueError(f"Invalid config format in {target_path}: {e}")

try:
    _current_settings = AppConfig()
except Exception:
    _current_settings = None 

def get_settings() -> AppConfig:
    if _current_settings is None:
        raise RuntimeError("Config is not loaded properly.")
    return _current_settings

def load_from_file(path: str):
    global _current_settings
    _current_settings = AppConfig(path)