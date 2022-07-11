from typing import Dict, Set
from xml.etree.ElementTree import Element

from pythonbible import get_verse_id

from pythonbible_parser.osis.util import (
    get_element_tail,
    get_element_text,
    get_element_text_and_tail,
    parse_osis_id,
    strip_namespace_from_tag,
)


class OSISBookParser:
    def __init__(
        self,
        root: Element,
        html_offset: int,
        html_readers_offset: int,
        html_notes_offset: int,
        plain_text_offset: int,
        plain_text_readers_offset: int,
        plain_text_notes_offset: int,
    ) -> None:
        self.root: Element = root
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

        self.html_verse_start_indeces: Dict[int, int] = {}
        self.html_readers_verse_start_indeces: Dict[int, int] = {}
        self.html_notes_verse_start_indeces: Dict[int, int] = {}
        self.plain_text_verse_start_indeces: Dict[int, int] = {}
        self.plain_text_readers_verse_start_indeces: Dict[int, int] = {}
        self.plain_text_notes_verse_start_indeces: Dict[int, int] = {}

        self.html_verse_end_indeces: Dict[int, int] = {}
        self.html_readers_verse_end_indeces: Dict[int, int] = {}
        self.html_notes_verse_end_indeces: Dict[int, int] = {}
        self.plain_text_verse_end_indeces: Dict[int, int] = {}
        self.plain_text_readers_verse_end_indeces: Dict[int, int] = {}
        self.plain_text_notes_verse_end_indeces: Dict[int, int] = {}

        self.current_verse: int = 0

        self.unknown_tags: Set = set()

    def parse(self) -> None:
        self._process_element(self.root, False)
        self._set_verse_end_indeces()

    def _process_element(self, element: Element, in_notes: bool) -> None:
        tag: str = strip_namespace_from_tag(element.tag)

        if tag == "div":
            self._process_children(element, in_notes)
            return

        if tag == "p":
            self._handle_paragraph(element)
            return

        if tag == "chapter":
            self._handle_chapter()
            return

        if tag == "title":
            self._handle_title(element)
            return

        if tag == "verse":
            self._append_text(get_element_text(element), in_notes)
            self._handle_verse(element)
            self._append_text(get_element_tail(element), in_notes)
            return

        if tag in {"w", "transChange"}:
            self._append_text(get_element_text_and_tail(element), in_notes)
            return

        if tag == "q":
            self._append_text(get_element_text(element), in_notes)
            self._process_children(element, in_notes)
            self._append_text(get_element_tail(element), in_notes)
            return

        if tag == "lg":
            # TODO - figure out poetic material formatting
            self._process_children(element, in_notes)
            return

        if tag == "l":
            # TODO - figure out poetic material formatting
            self._process_children(element, in_notes)
            return

        if tag == "lb":
            # TODO - insert line break
            self._append_text(get_element_text_and_tail(element), in_notes)
            return

        if tag == "list":
            # TODO - formatting?
            self._process_children(element, in_notes)
            return

        if tag == "item":
            # TODO - formatting?
            self._process_children(element, in_notes)
            return

        if tag == "seg":
            # TODO ?
            self._process_children(element, in_notes)
            self._append_text(get_element_tail(element), in_notes)
            return

        if tag == "divineName":
            # TODO ?
            self._process_children(element, in_notes)
            return

        if tag == "note":
            self._process_children(element, True)
            return

        if tag == "rdg" and in_notes:
            self._append_text(get_element_text(element), in_notes)
            return

        else:
            self.unknown_tags.add(tag)

    def _process_children(self, element: Element, in_notes: bool) -> None:
        for child in element:
            self._process_element(child, in_notes)

    def _handle_paragraph(self, element: Element) -> None:
        self.html += "<p>"
        self.html_readers += "<p>"
        self.html_notes += "<p>"
        self.plain_text += "\n"
        self.plain_text_readers += "\n"
        self.plain_text_notes += "\n"

        self._process_children(element, False)

        self.html += "</p>"
        self.html_readers += "</p>"
        self.html_notes += "</p>"

    def _handle_chapter(self) -> None:
        self._set_verse_end_indeces()
        self.current_verse = 0

    def _handle_title(self, element: Element) -> None:
        if self.title and self.short_title:
            return

        self.title = element.text or ""
        self.short_title = element.get("short") or ""

    def _handle_verse(self, element: Element) -> None:
        osis_id_str = element.get("osisID")

        if osis_id_str is None:
            return

        osis_id = parse_osis_id(element.get("osisID"))

        self._set_verse_end_indeces()

        self.current_verse = get_verse_id(osis_id.book, osis_id.chapter, osis_id.verse)

        self._set_verse_start_indeces()

        if (
            self.html
            and not self.html.endswith("</p>")
            and not self.html.endswith("<p>")
        ):
            self.html += " "

        self.html += f"<sup>{osis_id.verse}</sup>"

        if (
            self.html_notes
            and not self.html_notes.endswith("</p>")
            and not self.html_notes.endswith("<p>")
        ):
            self.html_notes += " "

        self.html_notes += f"<sup>{osis_id.verse}</sup>"

        if self.plain_text and not self.plain_text.endswith("\n"):
            self.plain_text += " "

        self.plain_text += f"{osis_id.verse}."

        if self.plain_text_notes and not self.plain_text_notes.endswith("\n"):
            self.plain_text_notes += " "

        self.plain_text_notes += f"{osis_id.verse}."

    def _append_text(self, text, in_notes: bool = False) -> None:
        if text is None:
            return

        text = text.strip()
        text = text.replace("¶", "")

        if len(text) == 0:
            return

        if text[0].isalpha():
            if not in_notes:
                if (
                    self.html
                    and not self.html.endswith("<br/>")
                    and not self.html.endswith("</p>")
                ):
                    self.html += " "

                if (
                    self.html_readers
                    and not self.html_readers.endswith("<br/>")
                    and not self.html_readers.endswith("</p>")
                ):
                    self.html_readers += " "

                if self.plain_text and not self.plain_text.endswith("\n"):
                    self.plain_text += " "

                if self.plain_text_readers and not self.plain_text_readers.endswith(
                    "\n"
                ):
                    self.plain_text_readers += " "

            if (
                self.html_notes
                and not self.html_notes.endswith("<br/>")
                and not self.html_notes.endswith("</p>")
            ):
                self.html_notes += " "

            if self.plain_text_notes and not self.plain_text_notes.endswith("\n"):
                self.plain_text_notes += " "

        if not in_notes:
            self.html += text
            self.html_readers += text
            self.plain_text += text
            self.plain_text_readers += text

        self.html_notes += text
        self.plain_text_notes += text

    def _set_verse_end_indeces(self) -> None:
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

    def _set_verse_start_indeces(self) -> None:
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
