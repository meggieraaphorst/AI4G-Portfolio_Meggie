"""Tests for clearforme.py. No API key needed: Gemini is replaced by a fake client
that returns real google-genai response and error objects."""

import json
from types import SimpleNamespace

import httpx
import pytest
from google.genai import errors, types

import clearforme as cfm

GOOD_ANSWER = {
    "language": "nl",
    "simple_explanation": "  De gemeente heeft uw aanvraag ontvangen.\n\nStuur de papieren voor 26 september 2026.  ",
    "action_needed": True,
    "actions": ["Stuur uw bankafschriften op voor 26 september 2026.", "  "],
    "difficult_words": [
        {"term": "bescheiden", "explanation": "Papieren of documenten."},
        {"term": "", "explanation": "Lege term wordt overgeslagen."},
    ],
}


def make_response(data=GOOD_ANSWER, finish_reason=types.FinishReason.STOP, parts=None, block_reason=None):
    raw = data if isinstance(data, str) else json.dumps(data)
    return types.GenerateContentResponse(
        candidates=[
            types.Candidate(
                content=types.Content(role="model", parts=parts if parts is not None else [types.Part(text=raw)]),
                finish_reason=finish_reason,
            )
        ],
        prompt_feedback=types.GenerateContentResponsePromptFeedback(block_reason=block_reason)
        if block_reason
        else None,
    )


class FakeClient:
    """Looks like genai.Client for the one call ClearForMe makes.

    `result` is returned (or raised) on every call; a list gives one item per call.
    """

    def __init__(self, result):
        self.results = list(result) if isinstance(result, list) else None
        self.result = result
        self.calls = []
        self.models = SimpleNamespace(generate_content=self._generate_content)

    def _generate_content(self, **kwargs):
        self.calls.append(kwargs)
        result = self.results.pop(0) if self.results is not None else self.result
        if isinstance(result, Exception):
            raise result
        return result

    @property
    def models_tried(self):
        return [call["model"] for call in self.calls]


# --- 1. Input checks -----------------------------------------------------------------


@pytest.mark.parametrize("text", [None, "", "   \n\t "])
def test_empty_input_is_rejected(text):
    with pytest.raises(cfm.InputError, match="paste a text"):
        cfm.check_input(text)


def test_too_long_input_is_rejected_with_the_numbers():
    with pytest.raises(cfm.InputError) as error:
        cfm.check_input("a" * (cfm.MAX_INPUT_CHARS + 1))
    assert f"{cfm.MAX_INPUT_CHARS + 1:,}" in str(error.value)
    assert f"{cfm.MAX_INPUT_CHARS:,}" in str(error.value)


def test_input_at_the_limit_is_accepted_and_stripped():
    text = "a" * cfm.MAX_INPUT_CHARS
    assert cfm.check_input(f"  {text}\n") == text


# --- 2. Privacy filter ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected, counts",
    [
        ("BSN: 123456782.", "BSN: [BSN].", {"BSN": 1}),
        ("BSN 1234.56.782", "BSN [BSN]", {"BSN": 1}),
        ("Nummer 123456789", "Nummer 123456789", {}),  # fails the elfproef
        ("Bedrag 1.250.000 euro", "Bedrag 1.250.000 euro", {}),
        ("Naar NL91 ABNA 0417 1643 00 t.n.v. de gemeente", "Naar [IBAN] t.n.v. de gemeente", {"IBAN": 1}),
        ("Rekening NL91ABNA0417164300", "Rekening [IBAN]", {"IBAN": 1}),
        ("Rekening NL00 ABNA 0417 1643 00", "Rekening NL00 ABNA 0417 1643 00", {}),  # bad checksum
        ("Mail jan.jansen+post@example.nl vandaag", "Mail [EMAIL] vandaag", {"EMAIL": 1}),
        ("Postbus 100, 2500 EA Den Haag / 2511AB", "Postbus 100, [POSTCODE] Den Haag / [POSTCODE]", {"POSTCODE": 2}),
        ("Betaal voor 15-10-2026 om 9.00 uur € 45,50", "Betaal voor 15-10-2026 om 9.00 uur € 45,50", {}),
    ],
)
def test_redact_personal_info(text, expected, counts):
    assert cfm.redact_personal_info(text) == (expected, counts)


def test_find_personal_info_reports_without_changing_the_text():
    text = "BSN: 123456782, mail jan@example.nl, postbus 2500 EA Den Haag."
    assert cfm.find_personal_info(text) == {"EMAIL": 1, "BSN": 1, "POSTCODE": 1}
    assert cfm.find_personal_info("Gewoon een brief zonder gegevens.") == {}


# --- 2b. Reading a web page ------------------------------------------------------------------


@pytest.mark.parametrize(
    "typed, expected",
    [
        ("https://www.gemeente.nl/brief", "https://www.gemeente.nl/brief"),
        ("  http://example.org/a?b=1  ", "http://example.org/a?b=1"),
        ("www.gemeente.nl/brief", "https://www.gemeente.nl/brief"),  # no scheme: add https
        ("Kijk op https://www.gemeente.nl voor meer info", None),  # a sentence, not a link
        ("Geachte heer/mevrouw, u moet betalen.", None),
        ("gemeente.nl", None),  # too vague to treat as a link
        ("file:///C:/Users/sam/geheim.txt", None),
        ("", None),
    ],
)
def test_looks_like_url(typed, expected):
    assert cfm.looks_like_url(typed) == expected


PAGE_HTML = """
<html><head><title>Bijzondere bijstand</title><style>p {color: red}</style></head>
<body>
  <nav>Menu | Zoeken | Inloggen</nav>
  <main>
    <h1>Aanvraag bijzondere bijstand</h1>
    <p>U moet de bescheiden    uiterlijk 26 september 2026 inleveren.</p>
    <p>Het bedrag is &euro; 450,00.</p>
    <p>Stuur afschriften van al uw bankrekeningen mee, samen met een offerte of
       aankoopbewijs en een kopie van een geldig identiteitsbewijs. Levert u de
       gegevens niet op tijd in, dan kan de gemeente uw aanvraag buiten behandeling
       laten. Heeft u vragen, neem dan contact op met uw consulent.</p>
  </main>
  <footer>Copyright gemeente</footer>
  <script>console.log("tracking")</script>
</body></html>
"""


def test_html_to_text_keeps_the_content_and_drops_the_rest():
    text = cfm.html_to_text(PAGE_HTML)
    assert "Bijzondere bijstand" in text  # the page title
    assert "uiterlijk 26 september 2026" in text
    assert "€ 450,00" in text
    assert "Menu" not in text and "Copyright" not in text and "tracking" not in text
    assert "    " not in text  # whitespace is cleaned up


def fake_client(handler):
    """An httpx client that answers from a function instead of the internet."""
    return httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)


def page_response(request, html=PAGE_HTML, content_type="text/html", status=200):
    return httpx.Response(status, headers={"content-type": content_type}, text=html)


PUBLIC_URL = "https://93.184.216.34/brief"  # an IP, so the tests never need DNS


def test_fetch_page_text_reads_a_normal_page():
    text = cfm.fetch_page_text(PUBLIC_URL, client=fake_client(page_response))
    assert "uiterlijk 26 september 2026" in text


@pytest.mark.parametrize(
    "url, message",
    [
        ("http://127.0.0.1:8501/secret", cfm.MSG_URL_LOCAL),
        ("http://localhost/secret", cfm.MSG_URL_LOCAL),
        ("http://10.0.0.5/router", cfm.MSG_URL_LOCAL),
        ("http://169.254.169.254/latest/meta-data/", cfm.MSG_URL_LOCAL),  # cloud metadata
        ("ftp://93.184.216.34/file.txt", cfm.MSG_URL_BAD),
    ],
)
def test_fetch_page_text_refuses_addresses_that_are_not_public_web_pages(url, message):
    calls = []

    def handler(request):
        calls.append(request)
        return page_response(request)

    with pytest.raises(cfm.FetchError) as error:
        cfm.fetch_page_text(url, client=fake_client(handler))
    assert str(error.value) == message
    assert calls == []  # nothing was even requested


def test_fetch_page_text_checks_the_address_again_after_a_redirect():
    def handler(request):
        if request.url.host == "93.184.216.34":
            return httpx.Response(301, headers={"location": "http://127.0.0.1/secret"})
        return page_response(request)

    with pytest.raises(cfm.FetchError) as error:
        cfm.fetch_page_text(PUBLIC_URL, client=fake_client(handler))
    assert str(error.value) == cfm.MSG_URL_LOCAL


def test_fetch_page_text_follows_a_normal_redirect():
    def handler(request):
        if request.url.path == "/brief":
            return httpx.Response(302, headers={"location": "https://93.184.216.34/echte-brief"})
        return page_response(request)

    assert "26 september 2026" in cfm.fetch_page_text(PUBLIC_URL, client=fake_client(handler))


@pytest.mark.parametrize(
    "response_maker, message",
    [
        (lambda request: page_response(request, status=404), cfm.MSG_URL_FAILED),
        (lambda request: page_response(request, content_type="application/pdf"), cfm.MSG_URL_NOT_A_PAGE),
        (lambda request: page_response(request, html="<html><body><p>Hoi</p></body></html>"), cfm.MSG_URL_NO_TEXT),
        (lambda request: (_ for _ in ()).throw(httpx.ConnectError("no route", request=request)), cfm.MSG_URL_FAILED),
        (lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("too slow", request=request)), cfm.MSG_URL_TIMEOUT),
    ],
)
def test_fetch_page_text_problems_become_friendly_messages(response_maker, message):
    with pytest.raises(cfm.FetchError) as error:
        cfm.fetch_page_text(PUBLIC_URL, client=fake_client(response_maker))
    assert str(error.value) == message


def test_fetch_page_text_stops_downloading_very_big_pages():
    huge = "<html><body>" + ("<p>Heel veel tekst. </p>" * 200_000) + "</body></html>"
    text = cfm.fetch_page_text(PUBLIC_URL, client=fake_client(lambda r: page_response(r, html=huge)))
    assert len(text) < len(huge)  # only the first part was downloaded


def test_shorten_for_input():
    short = "Korte tekst."
    assert cfm.shorten_for_input(short) == (short, False)

    long_text = ("Alinea met tekst.\n\n" * 2000)[: cfm.MAX_INPUT_CHARS + 500]
    shortened, was_shortened = cfm.shorten_for_input(long_text)
    assert was_shortened
    assert len(shortened) <= cfm.MAX_INPUT_CHARS
    assert shortened.endswith("Alinea met tekst.")  # cut at the end of a paragraph


# --- 4. Checking the answer ------------------------------------------------------------------


def test_good_answer_is_parsed_and_cleaned():
    result = cfm.parse_answer(make_response())
    assert result.language == "nl"
    assert result.simple_explanation.startswith("De gemeente")
    assert result.simple_explanation.endswith("2026.")
    assert result.actions == ["Stuur uw bankafschriften op voor 26 september 2026."]
    assert result.difficult_words == [cfm.DifficultWord("bescheiden", "Papieren of documenten.")]


def test_no_action_needed_gives_empty_action_list():
    result = cfm.parse_answer(make_response({**GOOD_ANSWER, "action_needed": False, "actions": []}))
    assert result.actions == []


def test_actions_are_kept_even_if_action_needed_is_false():
    result = cfm.parse_answer(make_response({**GOOD_ANSWER, "action_needed": False}))
    assert len(result.actions) == 1


def test_thinking_parts_are_ignored():
    parts = [types.Part(text="Let me think about this letter...", thought=True), types.Part(text=json.dumps(GOOD_ANSWER))]
    assert cfm.parse_answer(make_response(parts=parts)).language == "nl"


@pytest.mark.parametrize(
    "reason",
    [
        types.FinishReason.SAFETY,
        types.FinishReason.PROHIBITED_CONTENT,
        types.FinishReason.BLOCKLIST,
        types.FinishReason.SPII,
        types.FinishReason.RECITATION,
    ],
)
def test_blocked_answer_is_not_shown(reason):
    with pytest.raises(cfm.ExplainError) as error:
        cfm.parse_answer(make_response(finish_reason=reason))
    assert str(error.value) == cfm.MSG_REFUSED


def test_blocked_prompt_is_not_shown():
    response = types.GenerateContentResponse(
        prompt_feedback=types.GenerateContentResponsePromptFeedback(block_reason=types.BlockedReason.SAFETY)
    )
    with pytest.raises(cfm.ExplainError) as error:
        cfm.parse_answer(response)
    assert str(error.value) == cfm.MSG_REFUSED


def test_cut_off_answer_is_rejected():
    with pytest.raises(cfm.ExplainError) as error:
        cfm.parse_answer(make_response(finish_reason=types.FinishReason.MAX_TOKENS))
    assert str(error.value) == cfm.MSG_CUT_OFF


def test_other_language_gets_its_own_message():
    data = {**GOOD_ANSWER, "language": "other", "simple_explanation": "", "actions": []}
    with pytest.raises(cfm.UnsupportedLanguageError):
        cfm.parse_answer(make_response(data))


def test_language_finish_reason_gets_the_language_message():
    with pytest.raises(cfm.UnsupportedLanguageError):
        cfm.parse_answer(make_response(finish_reason=types.FinishReason.LANGUAGE))


@pytest.mark.parametrize(
    "data",
    [
        "Here is your explanation: ...",  # not JSON
        '{"language": "nl", "simple_expl',  # broken JSON
        "[1, 2, 3]",  # JSON, but not an object
        {k: v for k, v in GOOD_ANSWER.items() if k != "simple_explanation"},
        {k: v for k, v in GOOD_ANSWER.items() if k != "actions"},
        {k: v for k, v in GOOD_ANSWER.items() if k != "difficult_words"},
        {**GOOD_ANSWER, "language": "de"},
        {**GOOD_ANSWER, "simple_explanation": "   "},
        {**GOOD_ANSWER, "simple_explanation": 42},
        {**GOOD_ANSWER, "action_needed": True, "actions": []},
        {**GOOD_ANSWER, "actions": "Pay the bill"},
        {**GOOD_ANSWER, "difficult_words": ["bescheiden"]},
        {**GOOD_ANSWER, "difficult_words": [{"term": "Awb"}]},
    ],
)
def test_bad_answers_are_rejected_completely(data):
    with pytest.raises(cfm.BadAnswerError) as error:
        cfm.parse_answer(make_response(data))
    assert str(error.value) == cfm.MSG_BAD_ANSWER


@pytest.mark.parametrize(
    "response",
    [
        types.GenerateContentResponse(candidates=[]),
        make_response(parts=[]),
        make_response(parts=[types.Part(text="only thinking", thought=True)]),
        make_response(finish_reason=types.FinishReason.OTHER),
    ],
)
def test_empty_or_unexpected_responses_are_rejected(response):
    with pytest.raises(cfm.BadAnswerError):
        cfm.parse_answer(response)


# --- 5. Fact checks -------------------------------------------------------------------------

ORIGINAL = "Betaal € 450,00 uiterlijk 26 september 2026. Brief van 12-09-2026, zie ook October 15, 2026."


def test_nothing_missing_when_facts_are_copied():
    answer = "Betaal € 450,00 voor 26  September 2026. De brief is van 12-09-2026 en October 15, 2026."
    assert cfm.find_missing_facts(ORIGINAL, answer) == []


def test_missing_date_and_changed_amount_are_found():
    answer = "Betaal € 450 op tijd. De brief is van 12-09-2026 en October 15, 2026."
    assert cfm.find_missing_facts(ORIGINAL, answer) == ["26 september 2026", "€ 450,00"]


def test_a_date_split_over_two_lines_is_shown_on_one_line():
    # Web pages often break a date over lines; the warning should still read normally.
    assert cfm.find_missing_facts("Betaaldag: 15\n\nokt.\n2026", "Geen datum.") == ["15 okt. 2026"]


def test_amount_written_after_the_number_is_checked():
    assert cfm.find_missing_facts("U krijgt 1.250 euro.", "U krijgt geld.") == ["1.250 euro"]
    assert cfm.find_missing_facts("U krijgt 1.250 euro.", "U krijgt € 1.250.") == []


def test_invented_numbers_are_found():
    answer = "Betaal € 450,00 voor 30 september 2026."
    assert cfm.find_invented_numbers(ORIGINAL, answer) == ["30"]


def test_leading_zeros_do_not_count_as_invented():
    assert cfm.find_invented_numbers("Datum 05-09-2026", "Op 5 september 2026") == []


# --- The whole flow with a fake Gemini --------------------------------------------------------


def test_explain_sends_redacted_text_and_runs_the_checks():
    answer = {
        **GOOD_ANSWER,
        "simple_explanation": "Uw BSN is [BSN]. Stuur de papieren voor 26 september 2026. Betaal 99 euro.",
    }
    client = FakeClient(make_response(answer))

    result = cfm.explain(client, "BSN 123456782. Lever alles in voor 26 september 2026. Maximaal € 450,00.")

    sent = client.calls[0]
    assert "123456782" not in sent["contents"]
    assert "[BSN]" in sent["contents"]
    assert client.models_tried == [cfm.MODELS[0]]
    assert sent["config"].system_instruction == cfm.SYSTEM_PROMPT
    assert sent["config"].response_mime_type == "application/json"
    assert sent["config"].response_json_schema == cfm.RESPONSE_SCHEMA
    assert sent["config"].http_options.timeout == cfm.REQUEST_TIMEOUT_SECONDS * 1000
    assert result.model == cfm.MODELS[0]
    assert result.removed_info == {"BSN": 1}
    assert result.missing_facts == ["€ 450,00"]
    assert result.invented_numbers == ["99"]


def test_explain_does_not_call_gemini_for_empty_text():
    client = FakeClient(make_response())
    with pytest.raises(cfm.InputError):
        cfm.explain(client, "   ")
    assert client.calls == []


def test_make_client_turns_off_sdk_retries():
    # explain() tries the next model instead of retrying the same busy one.
    client = cfm.make_client("test-key")
    assert client._api_client._http_options.retry_options.attempts == 1


def api_error(cls, code, status, message="error", reason=None):
    error = {"code": code, "message": message, "status": status}
    if reason:
        error["details"] = [{"@type": "type.googleapis.com/google.rpc.ErrorInfo", "reason": reason}]
    return cls(code, {"error": error})


REQUEST = httpx.Request("POST", "https://generativelanguage.googleapis.com/")
# This is exactly what the real API returns when every free model is busy (seen on 2026-09-22).
BUSY = api_error(errors.ServerError, 503, "UNAVAILABLE", "This model is currently experiencing high demand.")


@pytest.mark.parametrize(
    "error",
    [
        BUSY,
        api_error(errors.ClientError, 429, "RESOURCE_EXHAUSTED"),
        api_error(errors.ClientError, 404, "NOT_FOUND"),
        httpx.ReadTimeout("timed out", request=REQUEST),
    ],
)
def test_next_model_is_tried_when_one_is_busy(error):
    client = FakeClient([error, make_response()])
    result = cfm.explain(client, "Een moeilijke brief.")
    assert client.models_tried == list(cfm.MODELS[:2])
    assert result.model == cfm.MODELS[1]


@pytest.mark.parametrize(
    "error, message",
    [
        (BUSY, cfm.MSG_SERVER),
        (api_error(errors.ClientError, 429, "RESOURCE_EXHAUSTED"), cfm.MSG_BUSY),
        (api_error(errors.ClientError, 404, "NOT_FOUND"), cfm.MSG_MODEL_UNAVAILABLE),
        (httpx.ReadTimeout("timed out", request=REQUEST), cfm.MSG_TIMEOUT),
    ],
)
def test_message_when_all_models_fail(monkeypatch, error, message):
    pauses = []
    monkeypatch.setattr(cfm.time, "sleep", pauses.append)
    client = FakeClient(error)
    with pytest.raises(cfm.ExplainError) as raised:
        cfm.explain(client, "Een moeilijke brief.")
    assert str(raised.value) == message
    assert client.models_tried == list(cfm.MODELS) * cfm.ROUNDS
    assert pauses == [cfm.PAUSE_BETWEEN_ROUNDS_SECONDS] * (cfm.ROUNDS - 1)


def test_all_models_are_tried_again_after_a_pause(monkeypatch):
    pauses = []
    monkeypatch.setattr(cfm.time, "sleep", pauses.append)
    client = FakeClient([BUSY] * len(cfm.MODELS) + [make_response()])
    result = cfm.explain(client, "Een moeilijke brief.")
    assert client.models_tried == list(cfm.MODELS) + [cfm.MODELS[0]]
    assert result.model == cfm.MODELS[0]
    assert pauses == [cfm.PAUSE_BETWEEN_ROUNDS_SECONDS]


@pytest.mark.parametrize(
    "error, message",
    [
        # This is exactly what the real API returns for a wrong key (checked on 2026-09-22).
        (
            api_error(errors.ClientError, 400, "INVALID_ARGUMENT",
                      "API key not valid. Please pass a valid API key.", reason="API_KEY_INVALID"),
            cfm.MSG_BAD_KEY,
        ),
        (api_error(errors.ClientError, 403, "PERMISSION_DENIED"), cfm.MSG_BAD_KEY),
        (api_error(errors.ClientError, 400, "INVALID_ARGUMENT", "Request contains an invalid argument."), cfm.MSG_GENERIC),
        (httpx.ConnectError("connection refused", request=REQUEST), cfm.MSG_NO_CONNECTION),
    ],
)
def test_errors_that_other_models_cannot_fix_stop_right_away(error, message):
    client = FakeClient(error)
    with pytest.raises(cfm.ExplainError) as raised:
        cfm.explain(client, "Een moeilijke brief.")
    assert str(raised.value) == message
    assert client.models_tried == [cfm.MODELS[0]]


def test_no_more_models_are_tried_when_the_time_budget_is_used_up(monkeypatch):
    clock = iter([0, 0, cfm.TIME_BUDGET_SECONDS - 2])  # start, first model, second model
    monkeypatch.setattr(cfm.time, "monotonic", lambda: next(clock))
    client = FakeClient(BUSY)
    with pytest.raises(cfm.ExplainError) as raised:
        cfm.explain(client, "Een moeilijke brief.")
    assert str(raised.value) == cfm.MSG_SERVER
    assert client.models_tried == [cfm.MODELS[0]]


def test_last_model_gets_only_the_time_that_is_left(monkeypatch):
    clock = iter([0, 0, cfm.TIME_BUDGET_SECONDS - 20])  # start, first model, second model
    monkeypatch.setattr(cfm.time, "monotonic", lambda: next(clock))
    client = FakeClient([BUSY, make_response()])
    cfm.explain(client, "Een moeilijke brief.")
    assert client.calls[1]["config"].http_options.timeout == 20 * 1000
