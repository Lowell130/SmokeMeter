import time
from bson import ObjectId

def now_ts() -> int:
    return int(time.time())

def oid(val: str) -> ObjectId:
    return ObjectId(val)

def to_primitive(value):
    """Converte ricorsivamente ObjectId e tipi non JSON in tipi primitivi."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: to_primitive(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_primitive(v) for v in value]
    return value
