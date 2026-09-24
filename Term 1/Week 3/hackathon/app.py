"""ClearForMe - difficult text, made clear.

Streamlit UI. Start it with:  streamlit run app.py
The logic (Gemini call, privacy filter, answer checks) is in clearforme.py.
"""

from __future__ import annotations

import html
import logging
import re

import streamlit as st

import clearforme as cfm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("clearforme.app")

PRIVACY_WARNING = (
    "Do not enter personal or confidential information. Remove names, addresses, "
    "BSN numbers and case numbers before submitting your text."
)
AI_WARNING = (
    "AI can make mistakes. Always check important information, dates and deadlines "
    "in the original text."
)
SPINNER_TEXT = "Reading your text and making it clear. This can take a minute or two..."
READING_SPINNER = "Opening the web page and reading it..."
NO_ACTION_TEXT = "The text does not ask you to do anything."
NO_WORDS_TEXT = "No difficult words found."

# How the privacy filter's placeholders are described to the user (singular, plural).
REMOVED_INFO_NAMES = {
    "BSN": ("BSN number", "BSN numbers"),
    "IBAN": ("bank account number", "bank account numbers"),
    "EMAIL": ("e-mail address", "e-mail addresses"),
    "POSTCODE": ("postcode", "postcodes"),
}

CSS = """
<style>
/* Less empty space at the top, so the text box and button fit on a phone screen. */
[data-testid="stMainBlockContainer"] { padding-top: 2.5rem; padding-bottom: 3rem; }
/* Hide Streamlit's "Press Ctrl+Enter to apply" hint: it is confusing here. */
[data-testid="InputInstructions"] { display: none; }
/* Darker text in yellow warnings: Streamlit's default only just passes WCAG AA. */
[data-testid="stAlertContentWarning"] p { color: #5C4300; }

[data-testid="stMarkdownContainer"] p.cfm-tagline {
    font-size: 1.35rem; color: #3D4A5C; margin: -0.75rem 0 0.25rem;
}

[data-testid="stTextArea"] label p { font-size: 1.15rem; font-weight: 600; }
[data-testid="stTextArea"] textarea { font-size: 1.1rem; line-height: 1.6; }
[data-testid="stButton"] button { min-height: 3.2rem; }
[data-testid="stButton"] button p { font-size: 1.2rem; font-weight: 600; }

/* The three result cards: same shape, different colour, so they are easy to tell apart. */
.cfm-card {
    border-left: 8px solid; border-radius: 12px;
    padding: 1.1rem 1.4rem; margin: 0;
    line-height: 1.65; color: #1A1A1A;
}
.cfm-card h2 { font-size: 1.4rem; font-weight: 700; line-height: 1.3; margin: 0 0 0.6rem; padding: 0; }
.cfm-card h2 span { margin-right: 0.45rem; }
.cfm-card p { margin: 0 0 0.75rem; }
.cfm-card p:last-child { margin-bottom: 0; }
.cfm-card ol { margin: 0; padding-left: 1.5rem; }
.cfm-card li { margin-bottom: 0.4rem; }
.cfm-card dl { margin: 0; padding: 0; }
.cfm-card dt { font-weight: 700; }
.cfm-card dd { margin: 0 0 0.75rem; }
.cfm-card dd:last-child { margin-bottom: 0; }

.cfm-explain { background: #EEF4FB; border-color: #1D4E89; }
.cfm-explain h2 { color: #1D4E89; }
.cfm-actions { background: #EDF7EF; border-color: #1E6B34; }
.cfm-actions h2 { color: #1E6B34; }
.cfm-words { background: #F5F0FA; border-color: #5B3A8C; }
.cfm-words h2 { color: #5B3A8C; }

@media (max-width: 480px) {
    .cfm-card { padding: 1rem 1.1rem; }
    .cfm-card h2 { font-size: 1.25rem; }
}
</style>
"""


# --- Helpers --------------------------------------------------------------------


def get_api_key() -> str | None:
    """Read the key from .streamlit/secrets.toml (or the Streamlit Cloud secrets)."""
    try:
        key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:  # there is no secrets file at all
        return None
    if not key or key == "paste-your-key-here":
        return None
    return key


def md_escape(text: str) -> str:
    """Escape text for st.markdown, so e.g. "$" or "*" in a date is shown as-is."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|$<>~:])", r"\\\1", text)


def paragraphs_html(text: str) -> str:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(f"<p>{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs)


def card(css_class: str, icon: str, title: str, body_html: str, lang: str) -> None:
    # Everything from the AI is escaped with html.escape before it gets here.
    st.html(
        f'<section class="cfm-card {css_class}">'
        f'<h2><span aria-hidden="true">{icon}</span>{title}</h2>'
        f'<div lang="{lang}">{body_html}</div>'
        "</section>"
    )


def join_and(items: list[str]) -> str:
    """["a", "b", "c"] -> "a, b and c" """
    return ", ".join(items[:-1]) + (" and " if len(items) > 1 else "") + items[-1]


def list_personal_info(found: dict[str, int]) -> str:
    """{"BSN": 1, "POSTCODE": 2} -> "1 BSN number and 2 postcodes" """
    items = []
    for placeholder, count in found.items():
        singular, plural = REMOVED_INFO_NAMES[placeholder]
        items.append(f"{count} {singular if count == 1 else plural}")
    return join_and(items)


def describe_removed_info(removed: dict[str, int]) -> str:
    shown = join_and([f"[{p}]" for p in removed])
    return (
        f"To protect your privacy, ClearForMe hid {list_personal_info(removed)} "
        f"before sending your text. In the explanation you see {shown} instead."
    )


def start_over() -> None:
    st.session_state["input_text"] = ""
    clear_result()


def clear_result() -> None:
    # A result or warning that belongs to a different text must not stay on screen.
    st.session_state.pop("result", None)
    st.session_state.pop("pending", None)


def confirm_hide_personal_info() -> None:
    # Runs when the user presses the button, before the page is drawn again.
    st.session_state["do_explain"] = True


# --- Main flow ---------------------------------------------------------------------


# Icons: only emoji, and only in messages. Streamlit's ":material/...:" icons are
# read aloud by screen readers as their code name (e.g. "auto_awesome").


def handle_submit(typed: str) -> None:
    """Called when the user presses "Make it clear". Nothing is sent before this."""
    try:
        text = cfm.check_input(typed)
    except cfm.InputError as e:
        st.warning(str(e))
        return

    # A link instead of a text: ClearForMe opens the page and reads it first.
    source_url = cfm.looks_like_url(text)
    page_shortened = False
    if source_url:
        with st.spinner(READING_SPINNER):
            try:
                text = cfm.fetch_page_text(source_url)
            except cfm.FetchError as e:
                st.error(str(e))
                return
            except Exception:
                log.exception("Unexpected error while reading %s", source_url)
                st.error(cfm.MSG_URL_FAILED)
                return
        text, page_shortened = cfm.shorten_for_input(text)

    # Stop before sending: the user decides what happens with personal information.
    found = cfm.find_personal_info(text)
    if found:
        st.session_state["pending"] = {
            "text": text,
            "found": found,
            "source_url": source_url,
            "page_shortened": page_shortened,
        }
        return

    explain_now(text, source_url, page_shortened)


def explain_now(text: str, source_url: str | None, page_shortened: bool) -> None:
    api_key = get_api_key()
    if not api_key:
        st.error(cfm.MSG_NO_KEY)
        return

    with st.spinner(SPINNER_TEXT):
        try:
            result = cfm.explain(cfm.make_client(api_key), text)
        except cfm.UnsupportedLanguageError as e:
            st.warning(str(e))
            return
        except cfm.ExplainError as e:
            st.error(str(e))
            return
        except Exception:
            log.exception("Unexpected error")
            st.error(cfm.MSG_GENERIC)
            return

    result.source_url = source_url or ""
    result.page_shortened = page_shortened
    st.session_state["result"] = result


def render_pending(pending: dict) -> None:
    """Warn about personal information. Nothing has been sent to the AI yet."""
    warning = st.container()  # keeps the warning above the button
    if st.button(
        "Hide it for me and make it clear",
        type="primary",
        width="stretch",
        on_click=confirm_hide_personal_info,
    ):
        return  # the warning disappears; the explanation is made in main()
    with warning:
        st.warning(
            "**Stop: your text contains personal information.**\n\n"
            f"ClearForMe found {list_personal_info(pending['found'])}. "
            "Nothing has been sent yet.\n\n"
            "Remove it from your text and press **Make it clear** again. "
            "Or let ClearForMe hide it for you: the AI then sees `[BSN]` instead of "
            "the real number.\n\n"
            "Watch out for names and street names as well: ClearForMe cannot find those.",
            icon="🛑",
        )


def render_result(result: cfm.Explanation) -> None:
    if result.source_url:
        st.caption(f"Explained from: {md_escape(result.source_url)}")
    if result.page_shortened:
        st.warning(cfm.MSG_PAGE_SHORTENED, icon="✂️")
    if result.removed_info:
        st.info(describe_removed_info(result.removed_info), icon="🛡️")

    if result.missing_facts or result.invented_numbers:
        sections = ["**Please check this in the original text.**"]
        if result.missing_facts:
            sections.append(
                "These dates or amounts are in your text, but not in the explanation:\n"
                + "\n".join(f"- {md_escape(fact)}" for fact in result.missing_facts)
            )
        if result.invented_numbers:
            sections.append(
                "These numbers are in the explanation, but we could not find them in your text:\n"
                + "\n".join(f"- {md_escape(n)}" for n in result.invented_numbers)
            )
        st.warning("\n\n".join(sections), icon="🔍")

    card("cfm-explain", "📝", "Simple explanation",
         paragraphs_html(result.simple_explanation), result.language)

    if result.actions:
        actions_html = "<ol>" + "".join(f"<li>{html.escape(a)}</li>" for a in result.actions) + "</ol>"
    else:
        actions_html = f"<p>{NO_ACTION_TEXT}</p>"
    card("cfm-actions", "✅", "What do I need to do?", actions_html, result.language)

    if result.difficult_words:
        words_html = "<dl>" + "".join(
            f"<dt>{html.escape(w.term)}</dt><dd>{html.escape(w.explanation)}</dd>"
            for w in result.difficult_words
        ) + "</dl>"
    else:
        words_html = f"<p>{NO_WORDS_TEXT}</p>"
    card("cfm-words", "📖", "Difficult words explained", words_html, result.language)

    st.warning(AI_WARNING, icon="⚠️")
    st.button("Start over", on_click=start_over, width="stretch")


def main() -> None:
    st.set_page_config(page_title="ClearForMe", page_icon="📄", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)

    st.title("ClearForMe", anchor=False)
    st.markdown('<p class="cfm-tagline">Difficult text, made clear.</p>', unsafe_allow_html=True)

    st.warning(PRIVACY_WARNING, icon="🔒")

    st.text_area(
        "Paste your difficult text or a link here",
        key="input_text",
        height=240,
        placeholder="For example a letter from the municipality or the tax office, "
        "an e-mail you do not understand, or a link to a web page (https://...).",
        help=f"You can paste up to {cfm.MAX_INPUT_CHARS:,} characters, or one web link.",
        on_change=clear_result,
    )

    # Nothing is sent to the AI until the user presses this button.
    if st.button("Make it clear", type="primary", width="stretch"):
        clear_result()
        handle_submit(st.session_state.get("input_text", ""))
    elif st.session_state.pop("do_explain", False):
        # The user chose to hide the personal information and continue.
        pending = st.session_state.pop("pending", None)
        if pending:
            explain_now(pending["text"], pending["source_url"], pending["page_shortened"])

    if "pending" in st.session_state:
        render_pending(st.session_state["pending"])

    if "result" in st.session_state:
        render_result(st.session_state["result"])


if __name__ == "__main__":
    main()
