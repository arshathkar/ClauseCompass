import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import yaml
import os

from app.privacy.checksums import luhn_checksum, verhoeff_checksum


@dataclass
class PII_Pattern:
    name: str
    regex: re.Pattern
    group: int = 0
    needs_context: bool = False
    validator: Optional[Callable[[str], bool]] = None
    optional: bool = False
    run_after: Optional[str] = None


def load_patterns(yaml_path: str | None = None) -> List[PII_Pattern]:
    if yaml_path is None:
        from app.core.settings import settings
        yaml_path = str(settings.data_dir / "pii_patterns.yaml")
    if not os.path.exists(yaml_path):
        return []
        
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    patterns_map = data.get('patterns', {})
    parsed_patterns = []
    
    validators = {
        'luhn': luhn_checksum,
        'verhoeff': verhoeff_checksum
    }
    
    for name, config in patterns_map.items():
        regex_str = config['regex']
        # Handle ignorecase inline flag properly for re.compile
        if regex_str.startswith('(?i)'):
            pattern = re.compile(regex_str[4:], re.IGNORECASE)
        else:
            pattern = re.compile(regex_str)
            
        validator = None
        if 'validator' in config:
            validator = validators.get(config['validator'])
            
        parsed_patterns.append(
            PII_Pattern(
                name=name,
                regex=pattern,
                group=config.get('group', 0),
                needs_context=config.get('needs_context', False),
                validator=validator,
                optional=config.get('optional', False),
                run_after=config.get('run_after')
            )
        )
        
    return parsed_patterns
