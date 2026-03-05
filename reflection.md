# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

The game did not behave as expected in several ways. The first issue I noticed was that return key did not trigger a form submission for my guess--submissions can only be made by clicking "Submit Guess", despite the UI messaging in the input field "Press Enter to apply". I also noticed that the input field had a red outline, suggesting an input validation error, even though I had entered a 3, which was within the valid input bounds based on the guidance in the UI.

Beyond that, testing with different inputs surfaced that seemingly no input would be considered a winning guess -- no matter what I entered, the messaging was "Go LOWER!".

Additionally, the "New Game" button no-ops.

Lastly, invalid inputs were not recognized as invalid. I can enter negative numbers, zero, or numbers greater than 100, and the input will be submitted.

---

Full analysis by Claude:

```
Bug 1: Enter key doesn't submit the form
----------------------------------------------------------------------------
Location: app.py:121-128

st.text_input and st.button are standalone widgets, not wrapped in a st.form. Streamlit only binds the Enter key to submission when both the input and submit button are inside a st.form / st.form_submit_button block. As written, pressing Enter triggers a Streamlit rerun but submit evaluates to False, so no guess is processed.


Bug 2: Red outline on valid input
----------------------------------------------------------------------------
Location: app.py:121-124

The st.text_input has no min_value/max_value constraints (those belong to st.number_input), but the absence of any explicit type parameter means Streamlit renders it as a plain text field. The red outline is likely a Streamlit/browser artifact from submitting or interacting with the form while the session state is in an inconsistent state — specifically because attempts initializes to 1 (app.py:96) and validation errors still increment the counter (app.py:148), which can leave the UI in a flagged state on rerender.


Bug 3: Hints are inverted AND secret type alternates, breaking win detection
----------------------------------------------------------------------------
Location: app.py:158-163, app.py:37-47

Two compounding bugs:

3a — Swapped hint messages: In check_guess, the messages are backwards:

if guess > secret:
    return "Too High", "📈 Go HIGHER!"   # ← should say Go LOWER
else:
    return "Too Low",  "📉 Go LOWER!"    # ← should say Go HIGHER
When the guess is too high, the player is told to go higher (worsening the situation). When too low, told to go lower — a feedback loop that traps the player.

3b — Secret alternates between int and str each attempt: Every time the attempt count is even, the secret is cast to a string before comparison:

if st.session_state.attempts % 2 == 0:
    secret = str(st.session_state.secret)  # attempts starts at 1, first submit → 2 (even!)
else:
    secret = st.session_state.secret
Since attempts starts at 1 and is incremented before the check, the very first guess always hits the even branch. An int compared to a str raises TypeError in Python 3, which falls into the except block and uses lexicographic string comparison — meaning "9" > "50" evaluates True and "3" > "42" evaluates False, producing wrong and inconsistent results. A correct guess (e.g., 42 == "42") is never True because an int never equals a string.


Bug 4: "New Game" button doesn't reset status
----------------------------------------------------------------------------
Location: app.py:134-138, app.py:140-145

The new_game handler resets attempts and secret but never resets st.session_state.status:

if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(1, 100)
    # status is never set back to "playing"
    st.rerun()
After a win or loss, status is "won" or "lost". On rerun, the guard at app.py:140 triggers st.stop() immediately, preventing any new game from proceeding.


Bug 5: No bounds validation on input
----------------------------------------------------------------------------
Location: app.py:14-29

parse_guess only checks that the input is parseable as a number. It never validates that the value falls within the game's range (low to high). There is no check like if value < low or value > high, so negative numbers, zero, and values above 100 (or above the difficulty ceiling) are silently accepted as valid guesses.


Bonus: Hard difficulty range is misconfigured
----------------------------------------------------------------------------
Location: app.py:9-10, app.py:136

get_range_for_difficulty("Hard") returns (1, 50) — a smaller range than Normal's (1, 100), making Hard easier to guess, not harder. Additionally, the "New Game" handler hardcodes random.randint(1, 100) regardless of difficulty, and the info message at app.py:110 always displays "1 and 100" regardless of the selected difficulty's actual range.
```

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
