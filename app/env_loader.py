"""
환경 변수 로더 모듈

이 모듈은 환경 변수에서 구성을 로드하는 기능을 제공합니다.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional


def get_env_var(name: str, default: Optional[Any] = None) -> Any:
    """
    환경 변수를 가져옵니다.
    
    Args:
        name: 환경 변수 이름
        default: 환경 변수가 없을 경우 반환할 기본값
        
    Returns:
        환경 변수 값 또는 기본값
    """
    return os.environ.get(name, default)


def replace_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    구성 딕셔너리의 모든 값에서 ${ENV_VAR} 형식의 환경 변수 참조를 실제 값으로 대체합니다.
    
    Args:
        config: 구성 딕셔너리
        
    Returns:
        환경 변수가 대체된 구성 딕셔너리
    """
    result = {}
    
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = replace_env_vars(value)
        elif isinstance(value, str):
            # ${ENV_VAR} 형식의 환경 변수 참조를 처리
            env_var_pattern = r'\${([A-Za-z0-9_]+)}'
            matches = re.findall(env_var_pattern, value)
            
            if matches:
                new_value = value
                for match in matches:
                    env_value = get_env_var(match)
                    if env_value is not None:
                        new_value = new_value.replace(f"${{{match}}}", env_value)
                result[key] = new_value
            else:
                result[key] = value
        else:
            result[key] = value
            
    return result 