"""Contains the OSISBookParser class."""
from __future__ import annotations

from typing import Any

from pythonbible import get_verse_id

from pythonbible_parser.osis.osis_utilities import (
    get_element_tail,
    get_element_text,
    get_element_text_and_tail,
    parse_osis_id,
    strip_namespace_from_tag,
)

HTML_P_OPEN = "<p>"
HTML_P_CLOSE = "</p>"
HTML_NEWLINE = "<br/>"

PLAIN_NEWLINE = "\n"


class OSISBookParser:
    """OSISBookParser parses an OSIS XML file for a specific book of the Bible."""

    def __init__(
        self: OSISBookParser,
        root: Any,
        html_offset: int,
        html_readers_offset: int,
        html_notes_offset: int,
        plain_text_offset: int,
        plain_text_readers_offset: int,
        plain_text_notes_offset: int,
    ) -> None:
        self.root: Any = root
        self.html_offset: int = html_offset
        self.html_readers_offset: int = html_readers_offset
        self.html_notes_offset: int = html_notes_offset
        self.plain_text_offset: int = plain_text_offset
        self.plain_text_readers_offset: int = plain_text_readers_offset
        self.plain_text_notes_offset: int = plain_text_notes_offset

        self.title: str = self.root.text or ""
        self.short_title: str = self.root.get("short") or ""

        self.html: str = ""
        self.html_readers: str = ""
        self.html_notes: str = ""
        self.plain_text: str = ""
        self.plain_text_readers: str = ""
        self.plain_text_notes: str = ""

        self.html_verse_start_indeces: dict[int, int] = {}
        self.html_readers_verse_start_indeces: dict[int, int] = {}
        self.html_notes_verse_start_indeces: dict[int, int] = {}
        self.plain_text_verse_start_indeces: dict[int, int] = {}
        self.plain_text_readers_verse_start_indeces: dict[int, int] = {}
        self.plain_text_notes_verse_start_indeces: dict[int, int] = {}

        self.html_verse_end_indeces: dict[int, int] = {}
        self.html_readers_verse_end_indeces: dict[int, int] = {}
        self.html_notes_verse_end_indeces: dict[int, int] = {}
        self.plain_text_verse_end_indeces: dict[int, int] = {}
        self.plain_text_readers_verse_end_indeces: dict[int, int] = {}
        self.plain_text_notes_verse_end_indeces: dict[int, int] = {}

        self.current_verse: int = 0

        self.unknown_tags: set[str] = set()

    def parse(self: OSISBookParser) -> None:
        self._process_element(self.root)
        self._set_verse_end_indeces()

    def _process_element(
        self: OSISBookParser,
        element: Any,
        in_notes: bool = False,
    ) -> None:
        tag: str = strip_namespace_from_tag(element.tag)

        self._handle_paragraph(element, tag)
        self._handle_chapter(tag)
        self._handle_title(element, tag)
        self._handle_verse(element, tag, in_notes)
        self._handle_q(element, tag, in_notes)
        self._handle_seg(element, tag, in_notes)
        self._handle_other_tags(element, tag, in_notes)

    def _process_children(
        self: OSISBookParser,
        element: Any,
        in_notes: bool = False,
    ) -> None:
        for child in element:
            self._process_element(child, in_notes)

    def _handle_paragraph(self: OSISBookParser, element: Any, tag: str) -> None:
        if tag != "p":
            return

        self.html += HTML_P_OPEN
        self.html_readers += HTML_P_OPEN
        self.html_notes += HTML_P_OPEN
        self.plain_text += PLAIN_NEWLINE
        self.plain_text_readers += PLAIN_NEWLINE
        self.plain_text_notes += PLAIN_NEWLINE

        self._process_children(element)

        self.html += HTML_P_CLOSE
        self.html_readers += HTML_P_CLOSE
        self.html_notes += HTML_P_CLOSE

    def _handle_chapter(self: OSISBookParser, tag: str) -> None:
        if tag != "chapter":
            return

        self._set_verse_end_indeces()
        self.current_verse = 0

    def _handle_title(self: OSISBookParser, element: Any, tag: str) -> None:
        if tag != "title":
            return

        if self.title and self.short_title:
            return

        self.title = element.text or ""
        self.short_title = element.get("short") or ""

    def _handle_verse(
        self: OSISBookParser,
        element: Any,
        tag: str,
        in_notes: bool,
    ) -> None:
        if tag != "verse":
            return

        self._append_text(get_element_text(element), in_notes)
        osis_id_str = element.get("osisID")

        if osis_id_str is None:
            return

        osis_id = parse_osis_id(element.get("osisID"))

        self._set_verse_end_indeces()

        self.current_verse = get_verse_id(osis_id.book, osis_id.chapter, osis_id.verse)

        self._set_verse_start_indeces()

        if (
            self.html
            and not self.html.endswith(HTML_P_CLOSE)
            and not self.html.endswith(HTML_P_OPEN)
        ):
            self.html += " "

        self.html += f"<sup>{osis_id.verse}</sup>"

        if (
            self.html_notes
            and not self.html_notes.endswith(HTML_P_CLOSE)
            and not self.html_notes.endswith(HTML_P_OPEN)
        ):
            self.html_notes += " "

        self.html_notes += f"<sup>{osis_id.verse}</sup>"

        if self.plain_text and not self.plain_text.endswith(PLAIN_NEWLINE):
            self.plain_text += " "

        self.plain_text += f"{osis_id.verse}."

        if self.plain_text_notes and not self.plain_text_notes.endswith(PLAIN_NEWLINE):
            self.plain_text_notes += " "

        self.plain_text_notes += f"{osis_id.verse}."
        self._append_text(get_element_tail(element), in_notes)

    def _handle_q(self: OSISBookParser, element: Any, tag: str, in_notes: bool) -> None:
        if tag != "q":
            return

        self._append_text(get_element_text(element), in_notes)
        self._process_children(element, in_notes)
        self._append_text(get_element_tail(element), in_notes)

    def _handle_seg(
        self: OSISBookParser,
        element: Any,
        tag: str,
        in_notes: bool,
    ) -> None:
        if tag != "seg":
            return

        self._process_children(element, in_notes)
        self._append_text(get_element_tail(element), in_notes)

    def _handle_other_tags(
        self: OSISBookParser,
        element: Any,
        tag: str,
        in_notes: bool,
    ) -> None:
        if tag in {"div", "lg", "l", "list", "item", "divineName", "note"}:
            # TODO - figure out poetical material formatting
            # TODO - figure out list formatting
            # TODO - figure out item formatting
            self._process_children(element, in_notes or tag == "note")
            return

        if tag in {"w", "transChange"}:
            self._append_text(get_element_text_and_tail(element), in_notes)
            return

        if tag == "lb":
            # TODO - insert line break
            self._append_text(get_element_text_and_tail(element), in_notes)
            return

        if tag == "rdg" and in_notes:
            self._append_text(get_element_text(element), in_notes)
            return

        self.unknown_tags.add(tag)

    def _append_text(self: OSISBookParser, text: str, in_notes: bool = False) -> None:
        text = text.strip() if text else ""
        text = text.replace("¶", "")

        if not text:
            return

        if text[0].isalpha():
            if not in_notes:
                if (
                    self.html
                    and not self.html.endswith(HTML_NEWLINE)
                    and not self.html.endswith(HTML_P_CLOSE)
                ):
                    self.html += " "

                if (
                    self.html_readers
                    and not self.html_readers.endswith(HTML_NEWLINE)
                    and not self.html_readers.endswith(HTML_P_CLOSE)
                ):
                    self.html_readers += " "

                if self.plain_text and not self.plain_text.endswith(PLAIN_NEWLINE):
                    self.plain_text += " "

                if self.plain_text_readers and not self.plain_text_readers.endswith(
                    PLAIN_NEWLINE,
                ):
                    self.plain_text_readers += " "

            if (
                self.html_notes
                and not self.html_notes.endswith(HTML_NEWLINE)
                and not self.html_notes.endswith(HTML_P_CLOSE)
            ):
                self.html_notes += " "

            if self.plain_text_notes and not self.plain_text_notes.endswith(
                PLAIN_NEWLINE,
            ):
                self.plain_text_notes += " "

        if not in_notes:
            self.html += text
            self.html_readers += text
            self.plain_text += text
            self.plain_text_readers += text

        self.html_notes += text
        self.plain_text_notes += text

    def _set_verse_end_indeces(self: OSISBookParser) -> None:
        if self.current_verse > 0:
            self.html_verse_end_indeces[self.current_verse] = (
                len(self.html) + self.html_offset
            )
            self.html_readers_verse_end_indeces[self.current_verse] = (
                len(self.html_readers) + self.html_readers_offset
            )
            self.html_notes_verse_end_indeces[self.current_verse] = (
                len(self.html_notes) + self.html_notes_offset
            )
            self.plain_text_verse_end_indeces[self.current_verse] = (
                len(self.plain_text) + self.plain_text_offset
            )
            self.plain_text_readers_verse_end_indeces[self.current_verse] = (
                len(self.plain_text_readers) + self.plain_text_readers_offset
            )
            self.plain_text_notes_verse_end_indeces[self.current_verse] = (
                len(self.plain_text_notes) + self.plain_text_notes_offset
            )

    def _set_verse_start_indeces(self: OSISBookParser) -> None:
        self.html_verse_start_indeces[self.current_verse] = (
            len(self.html) + self.html_offset
        )
        self.html_readers_verse_start_indeces[self.current_verse] = (
            len(self.html_readers) + self.html_readers_offset
        )
        self.html_notes_verse_start_indeces[self.current_verse] = (
            len(self.html_notes) + self.html_notes_offset
        )
        self.plain_text_verse_start_indeces[self.current_verse] = (
            len(self.plain_text) + self.plain_text_offset
        )
        self.plain_text_readers_verse_start_indeces[self.current_verse] = (
            len(self.plain_text_readers) + self.plain_text_readers_offset
        )
        self.plain_text_notes_verse_start_indeces[self.current_verse] = (
            len(self.plain_text_notes) + self.plain_text_notes_offset
        )
