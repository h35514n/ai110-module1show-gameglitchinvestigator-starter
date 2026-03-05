from logic_utils import check_guess, get_range_for_difficulty, parse_guess

def test_hard_range_is_harder_than_normal():
    # Bonus bug regression: Hard range was (1, 50), smaller than Normal's (1, 100)
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_too_high_message_says_lower():
    # Bug 3a regression: when guess is too high, message must say LOWER not HIGHER
    _, message = check_guess(60, 50)
    assert "LOWER" in message

def test_too_low_message_says_higher():
    # Bug 3a regression: when guess is too low, message must say HIGHER not LOWER
    _, message = check_guess(40, 50)
    assert "HIGHER" in message

def test_winning_guess_int_types():
    # Bug 3b regression: correct int guess against int secret must return Win,
    # not fall into string-comparison fallback due to type coercion
    outcome, _ = check_guess(42, 42)
    assert outcome == "Win"

def test_parse_guess_rejects_below_range():
    # Bug 5 regression: values below low must be rejected
    ok, _, err = parse_guess("0", low=1, high=100)
    assert not ok
    assert err is not None

def test_parse_guess_rejects_above_range():
    # Bug 5 regression: values above high must be rejected
    ok, _, err = parse_guess("101", low=1, high=100)
    assert not ok
    assert err is not None

def test_parse_guess_accepts_boundary_values():
    # Bug 5 regression: boundary values must be accepted
    ok_low, _, _ = parse_guess("1", low=1, high=100)
    ok_high, _, _ = parse_guess("100", low=1, high=100)
    assert ok_low
    assert ok_high

def test_no_win_on_type_mismatch():
    # Bug 3b regression: int guess vs str secret must NOT win via == comparison
    # (confirms the app must pass consistent types, not coerce secret to str)
    outcome, _ = check_guess(42, "42")
    assert outcome != "Win"
