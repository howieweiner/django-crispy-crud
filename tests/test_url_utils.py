from crudkit.utils.url_utils import remove_empty_url_params


class TestRemoveEmptyUrlParams:
    def test_removes_empty_params(self):
        assert remove_empty_url_params("q=&is_active=true") == "is_active=true"

    def test_keeps_non_empty_params(self):
        assert remove_empty_url_params("q=test&is_active=true") == "q=test&is_active=true"

    def test_empty_string_input(self):
        assert remove_empty_url_params("") == ""

    def test_all_empty_params(self):
        assert remove_empty_url_params("q=&is_active=") == ""
