"""UI tests for app.py, using Streamlit's built-in test runner. No API key needed."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import clearforme as cfm

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")

FAKE_RESULT = cfm.Explanation(
    language="nl",
    simple_explanation="De gemeente wil papieren van u.\n\nDat kost <b>niets</b>.",
    actions=["Stuur de papieren voor 26 september 2026."],
    difficult_words=[cfm.DifficultWord("bescheiden", "Papieren of documenten.")],
    removed_info={"BSN": 1, "POSTCODE": 2},
    missing_facts=["€ 450,00"],
    invented_numbers=["30"],
)


@pytest.fixture
def calls(monkeypatch):
    """Replace the Gemini call with a fake and record what it was asked."""
    calls = []

    def fake_explain(client, text):
        calls.append(text)
        return FAKE_RESULT

    monkeypatch.setattr(cfm, "explain", fake_explain)
    return calls


def start_app(api_key="test-key"):
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.secrets["GEMINI_API_KEY"] = api_key
    return at.run()


def button(at, label):
    return next(b for b in at.button if b.label == label)


def submit(at, text):
    at.text_area(key="input_text").input(text)
    button(at, "Make it clear").click()
    return at.run()


def cards(at):
    return [el.proto.body for el in at.get("html")]


def test_start_page_shows_header_privacy_warning_input_and_button():
    at = start_app()
    assert not at.exception
    assert at.title[0].value == "ClearForMe"
    assert "Difficult text, made clear." in at.markdown[-1].value
    assert at.warning[0].value.startswith("Do not enter personal or confidential information.")
    assert at.text_area(key="input_text").value == ""
    assert [b.label for b in at.button] == ["Make it clear"]  # no "Start over" yet
    assert cards(at) == []


def test_empty_text_gives_a_warning_and_no_api_call(calls):
    at = submit(start_app(), "   ")
    assert at.warning[-1].value == cfm.MSG_EMPTY
    assert calls == []


def test_too_long_text_gives_a_warning_and_no_api_call(calls):
    at = submit(start_app(), "a" * (cfm.MAX_INPUT_CHARS + 1))
    assert "too long" in at.warning[-1].value
    assert calls == []


@pytest.mark.parametrize("key", ["", "paste-your-key-here"])
def test_missing_api_key_gives_an_error_not_a_crash(calls, key):
    at = submit(start_app(api_key=key), "Een moeilijke brief.")
    assert not at.exception
    assert at.error[0].value == cfm.MSG_NO_KEY
    assert calls == []


def test_result_shows_three_cards_notices_and_disclaimer(calls):
    at = submit(start_app(), "Een moeilijke brief.")

    assert calls == ["Een moeilijke brief."]
    explain_card, actions_card, words_card = cards(at)
    assert "Simple explanation" in explain_card and 'lang="nl"' in explain_card
    assert "<p>De gemeente wil papieren van u.</p>" in explain_card
    assert "&lt;b&gt;niets&lt;/b&gt;" in explain_card  # AI text is escaped, not rendered as HTML
    assert "What do I need to do?" in actions_card
    assert "<li>Stuur de papieren voor 26 september 2026.</li>" in actions_card
    assert "Difficult words explained" in words_card
    assert "<dt>bescheiden</dt><dd>Papieren of documenten.</dd>" in words_card

    assert at.info[0].value.startswith("To protect your privacy, ClearForMe hid 1 BSN number and 2 postcodes")
    check = at.warning[1].value
    assert "€ 450,00" in check.replace("\\", "") and "30" in check
    assert at.warning[-1].value.startswith("AI can make mistakes.")
    assert [b.label for b in at.button] == ["Make it clear", "Start over"]


def test_no_actions_and_no_words_still_show_all_three_cards(monkeypatch):
    empty = cfm.Explanation("en", "Just information.", [], [])
    monkeypatch.setattr(cfm, "explain", lambda client, text: empty)
    at = submit(start_app(), "Some text.")
    _, actions_card, words_card = cards(at)
    assert "The text does not ask you to do anything." in actions_card
    assert "No difficult words found." in words_card


def test_start_over_clears_text_and_result(calls):
    at = submit(start_app(), "Een moeilijke brief.")
    button(at, "Start over").click()
    at.run()
    assert at.text_area(key="input_text").value == ""
    assert cards(at) == []
    assert [b.label for b in at.button] == ["Make it clear"]


def test_changing_the_text_removes_the_old_result(calls):
    at = submit(start_app(), "Een moeilijke brief.")
    at.text_area(key="input_text").input("Een andere brief.")
    at.run()
    assert cards(at) == []


# --- Stopping before personal information is sent ---------------------------------------


PERSONAL = "BSN 123456782. U moet de bescheiden uiterlijk 26 september 2026 inleveren."


def test_personal_information_stops_the_text_before_it_is_sent(calls):
    at = submit(start_app(), PERSONAL)
    assert calls == []  # nothing went to the AI
    assert at.warning[-1].value.startswith("**Stop: your text contains personal information.**")
    assert "1 BSN number" in at.warning[-1].value
    assert [b.label for b in at.button] == ["Make it clear", "Hide it for me and make it clear"]
    assert cards(at) == []


def test_user_can_let_the_app_hide_it_and_continue(calls):
    at = submit(start_app(), PERSONAL)
    button(at, "Hide it for me and make it clear").click()
    at.run()

    assert calls == [PERSONAL]  # explain() itself replaces the BSN before sending
    assert len(cards(at)) == 3
    assert not any(w.value.startswith("**Stop") for w in at.warning)


def test_editing_the_text_removes_the_stop_warning(calls):
    at = submit(start_app(), PERSONAL)
    at.text_area(key="input_text").input("Een brief zonder persoonsgegevens.")
    at.run()
    assert not any(w.value.startswith("**Stop") for w in at.warning)
    assert [b.label for b in at.button] == ["Make it clear"]


# --- Pasting a link ---------------------------------------------------------------------

LINK = "https://www.voorbeeldstad.nl/bijzondere-bijstand"
PAGE_TEXT = "Aanvraag bijzondere bijstand. U moet de gegevens uiterlijk 26 september 2026 opsturen."


@pytest.fixture
def page(monkeypatch):
    """Replace the real download with a fake page."""
    fetched = []

    def fake_fetch(url, client=None):
        fetched.append(url)
        return PAGE_TEXT

    monkeypatch.setattr(cfm, "fetch_page_text", fake_fetch)
    return fetched


def test_a_pasted_link_is_read_and_explained(calls, page):
    at = submit(start_app(), f"  {LINK}  ")
    assert page == [LINK]
    assert calls == [PAGE_TEXT]  # the page text went to the AI, not the link
    assert len(cards(at)) == 3


def test_the_link_is_shown_with_the_result(calls, page):
    at = submit(start_app(), LINK)
    captions = [c.value.replace("\\", "") for c in at.caption]  # undo markdown escaping
    assert f"Explained from: {LINK}" in captions


def test_a_long_page_is_shortened_with_a_warning(calls, monkeypatch):
    long_page = "Alinea met tekst.\n\n" * 2000
    monkeypatch.setattr(cfm, "fetch_page_text", lambda url, client=None: long_page)
    at = submit(start_app(), LINK)
    assert len(calls[0]) <= cfm.MAX_INPUT_CHARS  # only the first part was sent
    assert any(w.value == cfm.MSG_PAGE_SHORTENED for w in at.warning)


def test_a_page_that_cannot_be_read_gives_an_error_and_no_api_call(calls, monkeypatch):
    def failing_fetch(url, client=None):
        raise cfm.FetchError(cfm.MSG_URL_NOT_A_PAGE)

    monkeypatch.setattr(cfm, "fetch_page_text", failing_fetch)
    at = submit(start_app(), LINK)
    assert at.error[-1].value == cfm.MSG_URL_NOT_A_PAGE
    assert calls == []
    assert cards(at) == []


def test_text_that_only_mentions_a_link_is_treated_as_text(calls, page):
    typed = "Kijk op https://www.voorbeeldstad.nl voor meer informatie over bijstand."
    at = submit(start_app(), typed)
    assert page == []  # nothing was downloaded
    assert calls == [typed]
    assert len(cards(at)) == 3


@pytest.mark.parametrize(
    "error, element",
    [
        (cfm.UnsupportedLanguageError(cfm.MSG_UNSUPPORTED_LANGUAGE), "warning"),
        (cfm.ExplainError(cfm.MSG_BUSY), "error"),
        (cfm.BadAnswerError("missing keys"), "error"),
        (RuntimeError("bug"), "error"),
    ],
)
def test_errors_are_shown_as_messages_not_crashes(monkeypatch, error, element):
    def failing_explain(client, text):
        raise error

    monkeypatch.setattr(cfm, "explain", failing_explain)
    at = submit(start_app(), "Een moeilijke brief.")
    assert not at.exception
    expected = cfm.MSG_GENERIC if isinstance(error, RuntimeError) else str(error)
    assert getattr(at, element)[-1].value == expected
    assert cards(at) == []
