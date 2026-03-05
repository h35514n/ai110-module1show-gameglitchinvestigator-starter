import pytest

from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score


class TestGetRangeForDifficulty:
    def test_easy(self):
        assert get_range_for_difficulty("Easy") == (1, 20)

    def test_normal(self):
        assert get_range_for_difficulty("Normal") == (1, 100)

    def test_hard(self):
        assert get_range_for_difficulty("Hard") == (1, 200)

    def test_unknown_defaults_to_normal(self):
        assert get_range_for_difficulty("Unknown") == (1, 100)


class TestParseGuess:
    def test_valid_integer(self):
        ok, value, err = parse_guess("42", low=1, high=100)
        assert ok is True
        assert value == 42
        assert err is None

    def test_valid_float_truncated(self):
        ok, value, err = parse_guess("7.9", low=1, high=100)
        assert ok is True
        assert value == 7
        assert err is None

    def test_none_input(self):
        ok, value, err = parse_guess(None)
        assert ok is False
        assert value is None
        assert err == "Enter a guess."

    def test_empty_string(self):
        ok, value, err = parse_guess("")
        assert ok is False
        assert value is None
        assert err == "Enter a guess."

    def test_non_numeric(self):
        ok, value, err = parse_guess("abc")
        assert ok is False
        assert value is None
        assert err == "That is not a number."

    def test_below_low(self):
        ok, value, err = parse_guess("0", low=1, high=100)
        assert ok is False
        assert value is None
        assert "between 1 and 100" in err

    def test_above_high(self):
        ok, value, err = parse_guess("101", low=1, high=100)
        assert ok is False
        assert value is None
        assert "between 1 and 100" in err

    def test_boundary_low(self):
        ok, value, err = parse_guess("1", low=1, high=100)
        assert ok is True
        assert value == 1

    def test_boundary_high(self):
        ok, value, err = parse_guess("100", low=1, high=100)
        assert ok is True
        assert value == 100


class TestCheckGuess:
    def test_correct_guess(self):
        outcome, message = check_guess(50, 50)
        assert outcome == "Win"
        assert "Correct" in message

    def test_too_high(self):
        outcome, message = check_guess(80, 50)
        assert outcome == "Too High"
        assert "LOWER" in message

    def test_too_low(self):
        outcome, message = check_guess(20, 50)
        assert outcome == "Too Low"
        assert "HIGHER" in message

    def test_bad_input_type(self):
        outcome, message = check_guess(None, 50)
        assert outcome == "Bad Input"


class TestUpdateScore:
    def test_win_early(self):
        # attempt_number=1: points = 100 - 10*(1+1) = 80
        score = update_score(0, "Win", attempt_number=1)
        assert score == 80

    def test_win_minimum_points(self):
        # attempt_number=10: points = 100 - 10*11 = -10, clamped to 10
        score = update_score(0, "Win", attempt_number=10)
        assert score == 10

    def test_win_adds_to_existing_score(self):
        score = update_score(50, "Win", attempt_number=1)
        assert score == 130

    def test_too_high_even_attempt_adds_points(self):
        score = update_score(0, "Too High", attempt_number=2)
        assert score == 5

    def test_too_high_odd_attempt_subtracts_points(self):
        score = update_score(10, "Too High", attempt_number=1)
        assert score == 5

    def test_too_low_subtracts_points(self):
        score = update_score(10, "Too Low", attempt_number=3)
        assert score == 5

    def test_bad_input_no_score_change(self):
        score = update_score(42, "Bad Input", attempt_number=1)
        assert score == 42
