from __future__ import annotations

import re
from typing import Any


def parse_response_text(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}

    if text.lstrip().startswith("{"):
        import json
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    lines = text.split("\n")

    if lines[0].startswith("operationId:"):
        return _parse_flat_kv(lines)

    result: dict[str, Any] = {}
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        array_match = re.match(r"^data\[(\d+)\]\{(.+)\}:", line)
        if array_match:
            fields = [f.strip() for f in array_match.group(2).split(",")]
            i += 1
            rows = _parse_csv_rows(lines, i, indent=2, fields=fields)
            result["results"] = rows
            i += _count_indented(lines, i, 2)
            continue

        yaml_list_match = re.match(r"^data\[(\d+)\]:", line)
        if yaml_list_match:
            i += 1
            rows = _parse_yaml_list(lines, i, indent=2)
            result["results"] = rows
            i += _count_indented(lines, i, 2)
            continue

        if line == "data:":
            i += 1
            data, consumed = _parse_data_block(lines, i)
            result.update(data)
            i += consumed
            continue

        if line.startswith("success:"):
            i += 1
            continue

        kv_match = re.match(r"^(\S+?):\s*(.*)", line)
        if kv_match:
            result[kv_match.group(1)] = _coerce(kv_match.group(2))

        i += 1

    return result


def _parse_flat_kv(lines: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for line in lines:
        m = re.match(r"^(\S+?):\s*(.*)", line)
        if m:
            result[m.group(1)] = _coerce(m.group(2))
    return result


def _parse_data_block(lines: list[str], start: int) -> tuple[dict[str, Any], int]:
    return _parse_block(lines, start, indent=2)


def _parse_block(
    lines: list[str], start: int, indent: int
) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    prefix = " " * indent
    i = start
    while i < len(lines):
        line = lines[i]

        if not line.startswith(prefix):
            break
        if len(line) > len(prefix) and line[len(prefix)] == " ":
            break

        stripped = line[indent:]

        array_match = re.match(r"^(\w+)\[(\d+)\]\{(.+)\}:", stripped)
        if array_match:
            key = array_match.group(1)
            fields = [f.strip() for f in array_match.group(3).split(",")]
            i += 1
            rows = _parse_csv_rows(lines, i, indent=indent + 2, fields=fields)
            result[key] = rows
            i += _count_indented(lines, i, indent + 2)
            continue

        yaml_list_match = re.match(r"^(\w+)\[(\d+)\]:", stripped)
        if yaml_list_match:
            key = yaml_list_match.group(1)
            i += 1
            rows = _parse_yaml_list(lines, i, indent=indent + 2)
            result[key] = rows
            i += _count_indented(lines, i, indent + 2)
            continue

        kv_match = re.match(r"^(\S+?):\s*(.*)", stripped)
        if kv_match:
            key, val = kv_match.group(1), kv_match.group(2)
            if val:
                result[key] = _coerce(val)
                i += 1
            else:
                child_prefix = " " * (indent + 2)
                if i + 1 < len(lines) and lines[i + 1].startswith(child_prefix):
                    i += 1
                    nested, consumed = _parse_block(lines, i, indent + 2)
                    result[key] = nested
                    i += consumed
                else:
                    result[key] = None
                    i += 1
            continue

        i += 1

    return result, i - start


def _parse_yaml_list(
    lines: list[str], start: int, indent: int
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prefix = " " * indent
    item_prefix = prefix + "- "
    continuation_prefix = prefix + "  "
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.startswith(prefix):
            break
        if not line.strip():
            i += 1
            continue
        if line.startswith(item_prefix):
            row: dict[str, Any] = {}
            first_kv = line[len(item_prefix):]
            m = re.match(r"^(\S+?):\s*(.*)", first_kv)
            if m:
                row[m.group(1)] = _coerce(m.group(2))
            i += 1
            while i < len(lines):
                cline = lines[i]
                if not cline.startswith(continuation_prefix):
                    break
                if cline.startswith(item_prefix):
                    break
                stripped = cline[len(continuation_prefix):]
                cm = re.match(r"^(\S+?):\s*(.*)", stripped)
                if cm:
                    row[cm.group(1)] = _coerce(cm.group(2))
                i += 1
            rows.append(row)
        else:
            i += 1
    return rows


def _parse_csv_rows(
    lines: list[str], start: int, indent: int, fields: list[str]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    prefix = " " * indent
    i = start
    while i < len(lines):
        line = lines[i]
        if not line.startswith(prefix):
            break
        raw_row = line[indent:]
        if not raw_row.strip():
            i += 1
            continue
        values = _split_toon_row(raw_row)
        row: dict[str, Any] = {}
        for j, field in enumerate(fields):
            if j < len(values):
                row[field] = _coerce(values[j])
            else:
                row[field] = None
        rows.append(row)
        i += 1
    return rows


def _split_toon_row(line: str) -> list[str]:
    values: list[str] = []
    buf = ""
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "\\" and in_quotes and i + 1 < len(line):
            buf += ch + line[i + 1]
            i += 2
            continue
        if ch == '"':
            in_quotes = not in_quotes
            buf += ch
            i += 1
            continue
        if ch == "," and not in_quotes:
            values.append(buf.strip())
            buf = ""
            i += 1
            continue
        buf += ch
        i += 1
    if buf or values:
        values.append(buf.strip())
    return values


def _count_indented(lines: list[str], start: int, indent: int) -> int:
    prefix = " " * indent
    count = 0
    i = start
    while i < len(lines):
        if not lines[i].startswith(prefix) and lines[i].strip():
            break
        count += 1
        i += 1
    return count


def _coerce(value: str) -> Any:
    if not value:
        return None

    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null" or value == "None":
        return None

    try:
        n = int(value)
        if -9007199254740991 <= n <= 9007199254740991:
            return n
        return value
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass

    return value
