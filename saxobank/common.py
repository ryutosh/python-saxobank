from datetime import datetime
from functools import lru_cache
from typing import Dict


def auth_header(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@lru_cache()
def is_aware_datetime(target: datetime) -> bool:
    return bool(target.tzinfo and target.tzinfo.utcoffset(target))
