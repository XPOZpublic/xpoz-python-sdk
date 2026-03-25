def assert_has_fields(obj, expected_fields, entity_name=""):
    for field in expected_fields:
        assert hasattr(obj, field), f"{entity_name} missing field: {field}"


def assert_field_types(obj, field_type_map, entity_name=""):
    for field, expected_type in field_type_map.items():
        value = getattr(obj, field, None)
        if value is not None:
            assert isinstance(value, expected_type), (
                f"{entity_name}.{field}: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )


def assert_pagination_structure(result):
    assert result.pagination is not None, "pagination is None"
    p = result.pagination
    assert isinstance(p.total_rows, int), f"total_rows should be int, got {type(p.total_rows)}"
    assert isinstance(p.total_pages, int), f"total_pages should be int, got {type(p.total_pages)}"
    assert p.table_name is not None, "table_name is None"
    assert isinstance(p.table_name, str), f"table_name should be str, got {type(p.table_name)}"
