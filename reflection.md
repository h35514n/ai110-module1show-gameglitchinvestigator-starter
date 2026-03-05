# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

> - What did the game look like the first time you ran it?
> - List at least two concrete bugs you noticed at the start  
   (for example: "the secret number kept changing" or "the hints were backwards").


The game did not behave as expected in several ways. The first issue I noticed
was that return key did not trigger a form submission for my guess--submissions
can only be made by clicking "Submit Guess", despite the UI messaging in the
input field "Press Enter to apply". I also noticed that the input field had a
red outline, suggesting an input validation error, even though I had entered a
3, which was within the valid input bounds based on the guidance in the UI.

Beyond that, testing with different inputs surfaced that seemingly no input
would be considered a winning guess -- no matter what I entered, the messaging
was "Go LOWER!".

Additionally, the "New Game" button no-ops.

Lastly, invalid inputs were not recognized as invalid. I can enter negative
numbers, zero, or numbers greater than 100, and the input will be submitted.

<details>
<summary>Full analysis by Claude</summary>

```
Bug 1: Enter key doesn't submit the form
----------------------------------------------------------------------------
Location: app.py:121-128

st.text_input and st.button are standalone widgets, not wrapped in a st.form.
Streamlit only binds the Enter key to submission when both the input and submit
button are inside a st.form / st.form_submit_button block. As written, pressing
Enter triggers a Streamlit rerun but submit evaluates to False, so no guess is
processed.


Bug 2: Red outline on valid input
----------------------------------------------------------------------------
Location: app.py:121-124

The st.text_input has no min_value/max_value constraints (those belong to
st.number_input), but the absence of any explicit type parameter means Streamlit
renders it as a plain text field. The red outline is likely a Streamlit/browser
artifact from submitting or interacting with the form while the session state is
in an inconsistent state — specifically because attempts initializes to 1
(app.py:96) and validation errors still increment the counter (app.py:148),
which can leave the UI in a flagged state on rerender.


Bug 3: Hints are inverted AND secret type alternates, breaking win detection
----------------------------------------------------------------------------
Location: app.py:158-163, app.py:37-47

Two compounding bugs:

3a — Swapped hint messages: In check_guess, the messages are backwards:

When the guess is too high, the player is told to go higher (worsening the
situation). When too low, told to go lower — a feedback loop that traps the
player.

3b — Secret alternates between int and str each attempt: Every time the attempt
count is even, the secret is cast to a string before comparison:

Since attempts starts at 1 and is incremented before the check, the very first
guess always hits the even branch. An int compared to a str raises TypeError in
Python 3, which falls into the except block and uses lexicographic string
comparison — meaning "9" > "50" evaluates True and "3" > "42" evaluates False,
producing wrong and inconsistent results. A correct guess (e.g., 42 == "42") is
never True because an int never equals a string.


Bug 4: "New Game" button doesn't reset status
----------------------------------------------------------------------------
Location: app.py:134-138, app.py:140-145

The new_game handler resets attempts and secret but never resets
st.session_state.status:

After a win or loss, status is "won" or "lost". On rerun, the guard at
app.py:140 triggers st.stop() immediately, preventing any new game from
proceeding.


Bug 5: No bounds validation on input
----------------------------------------------------------------------------
Location: app.py:14-29

parse_guess only checks that the input is parseable as a number. It never
validates that the value falls within the game's range (low to high). There is
no check like if value < low or value > high, so negative numbers, zero, and
values above 100 (or above the difficulty ceiling) are silently accepted as
valid guesses.


Bonus: Hard difficulty range is misconfigured
----------------------------------------------------------------------------
Location: app.py:9-10, app.py:136

get_range_for_difficulty("Hard") returns (1, 50) — a smaller range than Normal's
(1, 100), making Hard easier to guess, not harder. Additionally, the "New Game"
handler hardcodes random.randint(1, 100) regardless of difficulty, and the info
message at app.py:110 always displays "1 and 100" regardless of the selected
difficulty's actual range.
```
</details>

---

## 2. How did you use AI as a teammate?

> - Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
> - Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
> - Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I used Claude in agent mode, with stepwise-confirmation, in VSCode.
Most suggestions were minimally correct -- all but one of its fixes were effective.

Claude only attempted one fix that did not work -- restoring the input field
focus after submission via a bit of JavaScript that would run in a `setTimeout`.
I thought this solution was hacky and pressed to find another way. The response
was that there was no other way without without implementing a custom component.
After testing it manually, I realized it no-oped anyway. Claude then asserted
that this was a known limitation of Streamlit.

Otherwise the only places where it fell short was in not catching all the bugs
on the first pass analyzing the code and in failing to spot an opportunity to
reduce duplication by extracting a helper. I'm also not sure the approach it
took to solving the UI bugs was the most elegant approach, but I don't know
Streamlit well enough to say for sure.

---

## 3. Debugging and testing your fixes

> - How did you decide whether a bug was really fixed?
> - Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
> - Did AI help you design or understand any tests? How?

I tested using the pytest suite and manually exercising the UI. With every fix I
asked Claude if adding a regression test would be appropriate -- in the
instances where the source of the bug was applciation logic rather than misuse
of Streamlit, it added the corresponding unit tests.

---

## 4. What did you learn about Streamlit and state?

> - In your own words, explain why the secret number kept changing in the original app.
> - How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
> - What change did you make that finally gave the game a stable secret number?

The secret number kept changing in part because it was being randomly selected
on every submission and in part because it was being stored in session state. A
Streamlit `rerun` clears the application state, so any state that you want to
persist across reruns must be stored in the session store.

---

## 5. Looking ahead: your developer habits

> - What is one habit or strategy from this project that you want to reuse in future labs or projects?
>   - This could be a testing habit, a prompting strategy, or a way you used Git.
> - What is one thing you would do differently next time you work with AI on a coding task?
> - In one or two sentences, describe how this project changed the way you think about AI generated code.

The key areas of friction I feel working in this fashion so far are in:

- Waiting for responses
- Testing (primarily manually, or running automated tests)

Something I took away from this as a habit to maintain in the future is to
manually identify opportunities for refactoring and also prompting for them.
The LLM seems to have a bias toward minimal changes, so it won't, for example,
apply refactorings like ExtractMethod unprompted.

The one thing I would do differently doing AI-coding is to be exercise more
control over the sequencing of work and to review more rigorously at every step
than I did this time. Claude did better than I expected identifying the bugs in
the code, but not as well as I thought, and giving it a wide berth early on made
it harder to reason about the code once it began making changes.

This project left me with the following update to my priors about AI-generated
code: My first encounters with AI-generated code left me skeptical, and it
wasn't until I had had several experiences of LLMs "one-shotting" various script
implementations in shell script and JavaScript that I grew more favorable to it.
This experience was a useful as a marginal corrective, back in the direction
toward skepticism. My sense so far is that LLMs need a lot more guidance and a
tighter leash when working on application code, legacy code, code that's
dependency-heavy. I haven't yet done any full agentic coding, but this has left
me curious to know how context is effectively tailored to enable agents to run
more independently.