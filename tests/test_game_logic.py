from logic_utils import check_guess

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

def test_no_win_on_type_mismatch():
    # Bug 3b regression: int guess vs str secret must NOT win via == comparison
    # (confirms the app must pass consistent types, not coerce secret to str)
    outcome, _ = check_guess(42, "42")
    assert outcome != "Win"
