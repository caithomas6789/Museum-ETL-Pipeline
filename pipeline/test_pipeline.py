from pipeline import check_date_and_time, check_exhibit, check_rating
from unittest.mock import patch


class TestDateTimeCheck:
    def test_valid_date_time(self):
        test_dict = {"at": '2023-11-14T13:12:08.882405+00:00'}

        assert check_date_and_time(test_dict) == ""

    def test_late_time(self):
        test_dict = {"at": '2023-11-14T18:30:08.882405+00:00'}

        assert check_date_and_time(test_dict) == "Invalid time - Too late"

    def test_early_time(self):
        test_dict = {"at": '2023-11-14T08:30:08.882405+00:00'}

        assert check_date_and_time(test_dict) == "Invalid time - Too early"

    def test_early_time(self):
        test_dict = {"at": '2023-11-14T08:30:08.882405+00:00'}

        assert check_date_and_time(test_dict) == "Invalid time - Too early"


class TestExhibitCheck:
    @patch('pipeline.get_max_exhibit_id')
    def test_valid_exhibit(self, mock_get_max_exhibit_id):
        mock_get_max_exhibit_id.return_value = 6

        test_dict = {"site": 2}

        assert check_exhibit(test_dict, "") == ""

    @patch('pipeline.get_max_exhibit_id')
    def test_invalid_exhibit(self, mock_get_max_exhibit_id):
        mock_get_max_exhibit_id.return_value = 6

        test_dict = {"site": 6}

        assert check_exhibit(test_dict, "") == "Invalid exhibit"

    @patch('pipeline.get_max_exhibit_id')
    def test_no_exhibit(self, mock_get_max_exhibit_id):
        mock_get_max_exhibit_id.return_value = 6

        test_dict = {}

        assert check_exhibit(test_dict, "") == "No exhibit"


class TestRatingCheck:
    def test_valid_rating(self):

        test_dict = {"val": 3}

        assert check_rating(test_dict, "") == ""

    def test_invalid_rating(self):

        test_dict = {"val": 6}

        assert check_rating(test_dict, "") == "Invalid rating"

    def test_no_rating(self):

        test_dict = {}

        assert check_rating(test_dict, "") == "No rating"

    def test_valid_assistance_or_emergency(self):

        test_dict = {"val": -1, "type": 0}

        assert check_rating(test_dict, "") == ""

    def test_invalid_assistance_or_emergency(self):

        test_dict = {"val": -1, "type": 5}

        assert check_rating(test_dict, "") == "Invalid emergency/assistance"
