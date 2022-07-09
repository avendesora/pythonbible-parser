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
        plain_text_offset: int,
        plain_text_readers_offset: int,
    ) -> None:
        self.root: Element = root
        self.html_offset: int = html_offset
        self.html_readers_offset: int = html_readers_offset
        self.plain_text_offset: int = plain_text_offset
        self.plain_text_readers_offset: int = plain_text_readers_offset

        self.title: str = self.root.text or ""
        self.short_title: str = self.root.get("short") or ""

        self.html: str = ""
        self.html_readers: str = ""
        self.plain_text: str = ""
        self.plain_text_readers: str = ""

        self.html_verse_start_indeces: Dict[int, int] = {}
        self.html_readers_verse_start_indeces: Dict[int, int] = {}
        self.plain_text_verse_start_indeces: Dict[int, int] = {}
        self.plain_text_readers_verse_start_indeces: Dict[int, int] = {}

        self.html_verse_end_indeces: Dict[int, int] = {}
        self.html_readers_verse_end_indeces: Dict[int, int] = {}
        self.plain_text_verse_end_indeces: Dict[int, int] = {}
        self.plain_text_readers_verse_end_indeces: Dict[int, int] = {}

        self.current_verse: int = 0

        self.unknown_tags: Set = set()

    def parse(self) -> None:
        self._process_element(self.root)
        self._set_verse_end_indeces()

    def _process_element(self, element: Element) -> None:
        tag: str = strip_namespace_from_tag(element.tag)

        if tag == "div":
            self._process_children(element)

        elif tag == "p":
            self._handle_paragraph(element)

        elif tag == "chapter":
            self._handle_chapter(element)

        elif tag == "title":
            self._handle_title(element)

        elif tag == "verse":
            self._append_text(get_element_text(element))
            self._handle_verse(element)
            self._append_text(get_element_tail(element))

        elif tag in {"w", "transChange"}:
            self._append_text(get_element_text_and_tail(element))

        elif tag == "q":
            self._append_text(get_element_text(element))
            self._process_children(element)
            self._append_text(get_element_tail(element))

        elif tag == "lg":
            # TODO - figure out poetic material formatting
            self._process_children(element)

        elif tag == "l":
            # TODO - figure out poetic material formatting
            self._process_children(element)

        elif tag == "lb":
            # TODO - insert line break
            self._append_text(get_element_text_and_tail(element))

        elif tag == "list":
            # TODO - formatting?
            self._process_children(element)

        elif tag == "item":
            # TODO - formatting?
            self._process_children(element)

        elif tag == "seg":
            # TODO ?
            self._process_children(element)
            self._append_text(get_element_tail(element))

        elif tag == "divineName":
            # TODO ?
            self._process_children(element)

        elif tag == "note":
            # ignore for now
            # TODO - notes (note, reference, rdg, rdgGroup)
            ...

        else:
            self.unknown_tags.add(tag)

    def _process_children(self, element):
        for child in element:
            self._process_element(child)

    def _handle_paragraph(self, element):
        self.html += "<p>"
        self.html_readers += "<p>"
        self.plain_text += "\n"
        self.plain_text_readers += "\n"

        self._process_children(element)

        self.html += "</p>"
        self.html_readers += "</p>"

    def _handle_chapter(self, element):
        self._set_verse_end_indeces()
        self.current_verse = 0

    def _handle_title(self, element):
        if self.title and self.short_title:
            return

        self.title = element.text or ""
        self.short_title = element.get("short") or ""

    def _handle_verse(self, element):
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

        if self.plain_text and not self.plain_text.endswith("\n"):
            self.plain_text += " "

        self.plain_text += f"{osis_id.verse}."

    def _append_text(self, text):
        if text is None:
            return

        text = text.strip()
        text = text.replace("¶", "")

        if len(text) == 0:
            return

        if text[0].isalpha():
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

            if self.plain_text_readers and not self.plain_text_readers.endswith("\n"):
                self.plain_text_readers += " "

        self.html += text
        self.html_readers += text
        self.plain_text += text
        self.plain_text_readers += text

    def _set_verse_end_indeces(self):
        if self.current_verse > 0:
            self.html_verse_end_indeces[self.current_verse] = (
                len(self.html) + self.html_offset
            )
            self.html_readers_verse_end_indeces[self.current_verse] = (
                len(self.html_readers) + self.html_readers_offset
            )
            self.plain_text_verse_end_indeces[self.current_verse] = (
                len(self.plain_text) + self.plain_text_offset
            )
            self.plain_text_readers_verse_end_indeces[self.current_verse] = (
                len(self.plain_text_readers) + self.plain_text_readers_offset
            )

    def _set_verse_start_indeces(self):
        self.html_verse_start_indeces[self.current_verse] = (
            len(self.html) + self.html_offset
        )
        self.html_readers_verse_start_indeces[self.current_verse] = (
            len(self.html_readers) + self.html_readers_offset
        )
        self.plain_text_verse_start_indeces[self.current_verse] = (
            len(self.plain_text) + self.plain_text_offset
        )
        self.plain_text_readers_verse_start_indeces[self.current_verse] = (
            len(self.plain_text_readers) + self.plain_text_readers_offset
        )
