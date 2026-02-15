import re

_CAMEL_TO_SNAKE_RE1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_TO_SNAKE_RE2 = re.compile(r"([a-z0-9])([A-Z])")


def camel_to_snake(name: str) -> str:
    s = _CAMEL_TO_SNAKE_RE1.sub(r"\1_\2", name)
    return _CAMEL_TO_SNAKE_RE2.sub(r"\1_\2", s).lower()


def snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def map_fields_to_camel(fields: list[str] | None) -> list[str] | None:
    if fields is None:
        return None
    return [snake_to_camel(f) for f in fields]


def map_dict_keys_to_snake(data: dict[str, object]) -> dict[str, object]:
    return {camel_to_snake(k): v for k, v in data.items()}


def map_list_of_dicts_to_snake(data: list[dict[str, object]]) -> list[dict[str, object]]:
    return [map_dict_keys_to_snake(item) for item in data]
