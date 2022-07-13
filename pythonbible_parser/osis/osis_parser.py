"""Contains the parser for OSIS format files."""

from __future__ import annotations

import os
from dataclasses import dataclass

import pythonbible as bible
from defusedxml import ElementTree

from pythonbible_parser.osis.constants import BOOK_IDS
from pythonbible_parser.osis.osis_book_parser import OSISBookParser
from pythonbible_parser.osis.util import get_namespace

INPUT_FOLDER: str = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "versions"
)
OUTPUT_FOLDER: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "output")

XPATH_BOOK: str = ".//xmlns:div[@osisID='{}']"


@dataclass
class VerseIndeces:
    start_index: int
    end_index: int


class OSISParser:
    """
    Parse files containing scripture text in the OSIS format.

    OSISParser extends BibleParser and contains all the functionality necessary
    to parse XML files that are in the OSIS format.
    """

    def __init__(self, version: bible.Version) -> None:
        """
        Initialize the OSIS parser.

        Set the version, the element tree from the appropriate version XML file,
        and the namespaces.

        :param version:
        """
        # super(OSISParser, self).__init__(version)
        self.version: bible.Version = version

        self.tree: ElementTree = ElementTree.parse(
            os.path.join(INPUT_FOLDER, f"{version.value.lower()}.xml")
        )
        self.namespaces: dict[str, str] = {
            "xmlns": get_namespace(self.tree.getroot().tag)
        }

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

    def parse(self):
        html_offset: int = 0
        html_readers_offset: int = 0
        html_notes_offset: int = 0
        plain_text_offset: int = 0
        plain_text_readers_offset: int = 0
        plain_text_notes_offset: int = 0

        for book in bible.Book:
            book_element = self._get_book_element(book)

            if book_element is None:
                continue

            book_parser = OSISBookParser(
                book_element,
                html_offset,
                html_readers_offset,
                html_notes_offset,
                plain_text_offset,
                plain_text_readers_offset,
                plain_text_notes_offset,
            )
            book_parser.parse()

            self.html += book_parser.html
            self.html_readers += book_parser.html_readers
            self.html_notes += book_parser.html_notes
            self.plain_text += book_parser.plain_text
            self.plain_text_readers += book_parser.plain_text_readers
            self.plain_text_notes += book_parser.plain_text_notes

            html_offset = len(self.html)
            html_readers_offset = len(self.html_readers)
            html_notes_offset = len(self.html_notes)
            plain_text_offset = len(self.plain_text)
            plain_text_readers_offset = len(self.plain_text_readers)
            plain_text_notes_offset = len(self.plain_text_notes)

            self.html_verse_start_indeces.update(book_parser.html_verse_start_indeces)
            self.html_readers_verse_start_indeces.update(
                book_parser.html_readers_verse_start_indeces
            )
            self.html_notes_verse_start_indeces.update(
                book_parser.html_notes_verse_start_indeces
            )
            self.plain_text_verse_start_indeces.update(
                book_parser.plain_text_verse_start_indeces
            )
            self.plain_text_readers_verse_start_indeces.update(
                book_parser.plain_text_readers_verse_start_indeces
            )
            self.plain_text_notes_verse_start_indeces.update(
                book_parser.plain_text_notes_verse_start_indeces
            )

            self.html_verse_end_indeces.update(book_parser.html_verse_end_indeces)
            self.html_readers_verse_end_indeces.update(
                book_parser.html_readers_verse_end_indeces
            )
            self.html_notes_verse_end_indeces.update(
                book_parser.html_notes_verse_end_indeces
            )
            self.plain_text_verse_end_indeces.update(
                book_parser.plain_text_verse_end_indeces
            )
            self.plain_text_readers_verse_end_indeces.update(
                book_parser.plain_text_readers_verse_end_indeces
            )
            self.plain_text_notes_verse_end_indeces.update(
                book_parser.plain_text_notes_verse_end_indeces
            )

    def write(self):
        version_str: str = self.version.value.lower()
        version_folder: str = os.path.join(OUTPUT_FOLDER, version_str)

        for folder in [OUTPUT_FOLDER, version_folder]:
            if not os.path.exists(folder):
                os.mkdir(folder)
        self._write_file(version_folder, "html.py", f"{version_str}_html", self.html)
        self._write_file(
            version_folder,
            "html_readers.py",
            f"{version_str}_html_readers",
            self.html_readers,
        )
        self._write_file(
            version_folder,
            "html_notes.py",
            f"{version_str}_html_notes",
            self.html_notes,
        )
        self._write_file(
            version_folder,
            "plain_text.py",
            f"{version_str}_plain_text",
            self.plain_text,
        )
        self._write_file(
            version_folder,
            "plain_text_readers.py",
            f"{version_str}_plain_text_readers",
            self.plain_text_readers,
        )
        self._write_file(
            version_folder,
            "plain_text_notes.py",
            f"{version_str}_plain_text_notes",
            self.plain_text_notes,
        )

    def _get_book_element(self, book: bible.Book):
        xpath: str = XPATH_BOOK.format(BOOK_IDS.get(book))
        return self.tree.find(xpath, namespaces=self.namespaces)

    @staticmethod
    def _write_file(folder, filename, variable, value):
        with open(os.path.join(folder, filename), "w") as writer:
            writer.write(f'{variable} = """{value}"""')
