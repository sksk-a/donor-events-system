from pathlib import Path
from app.utils.json_handler import JsonHandler


class TestJsonHandler:
    def test_read_json(self, tmp_path):
        file_path = tmp_path / "test.json"
        file_path.write_text('{"key": "value", "number": 42}', encoding='utf-8')

        handler = JsonHandler(str(file_path))
        data = handler.read_json()

        assert data["key"] == "value"
        assert data["number"] == 42

    def test_write_json(self, tmp_path):
        file_path = tmp_path / "output.json"
        handler = JsonHandler(str(file_path))

        test_data = {"name": "Test", "count": 10}
        handler.write_json(test_data)

        assert file_path.exists()
        content = handler.read_json()
        assert content["name"] == "Test"
        assert content["count"] == 10

    def test_append_to_list(self, tmp_path):
        file_path = tmp_path / "list_test.json"
        file_path.write_text('{"items": [{"id": 1}]}', encoding='utf-8')

        handler = JsonHandler(str(file_path))
        handler.append_to_list("items", {"id": 2, "name": "New"})

        data = handler.read_json()
        assert len(data["items"]) == 2
        assert data["items"][1]["id"] == 2

    def test_find_by_id(self, tmp_path):
        file_path = tmp_path / "find_test.json"
        file_path.write_text(
            '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}',
            encoding='utf-8'
        )

        handler = JsonHandler(str(file_path))
        found = handler.find_by_id("users", 2)

        assert found is not None
        assert found["name"] == "Bob"

        not_found = handler.find_by_id("users", 999)
        assert not_found is None

    def test_filter_by_field(self, tmp_path):
        file_path = tmp_path / "filter_test.json"
        file_path.write_text(
            '{"products": [{"id": 1, "category": "A"}, {"id": 2, "category": "B"}, {"id": 3, "category": "A"}]}',
            encoding='utf-8'
        )

        handler = JsonHandler(str(file_path))
        filtered = handler.filter_by_field("products", "category", "A")

        assert len(filtered) == 2
        assert all(item["category"] == "A" for item in filtered)

    def test_str_and_repr(self, tmp_path):
        file_path = tmp_path / "test.json"
        handler = JsonHandler(str(file_path))

        str_result = str(handler)
        assert "JsonHandler" in str_result
        assert str(file_path) in str_result

        repr_result = repr(handler)
        assert "JsonHandler" in repr_result
