"""Contains the parser for OSIS format files."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import pythonbible as bible
from defusedxml import ElementTree

from pythonbible_parser.osis.constants import BOOK_IDS
from pythonbible_parser.osis.osis_book_parser import OSISBookParser
from pythonbible_parser.osis.osis_utilities import get_namespace

CURRENT_FOLDER: str = os.path.realpath(__file__)
CURRENT_FOLDER_NAME: str = os.path.dirname(CURRENT_FOLDER)
INPUT_FOLDER: str = os.path.join(CURRENT_FOLDER_NAME, "versions")
OUTPUT_FOLDER: str = os.path.join(CURRENT_FOLDER_NAME, "output")

XPATH_BOOK: str = ".//xmlns:div[@osisID='{}']"


class OSISParser:
    """
    Parse files containing scripture text in the OSIS format.

    OSISParser extends BibleParser and contains all the functionality necessary
    to parse XML files that are in the OSIS format.
    """

    def __init__(self: OSISParser, version: bible.Version) -> None:
        """
        Initialize the OSIS parser.

        Set the version, the element tree from the appropriate version XML file,
        and the namespaces.

        :param version:
        """
        self.version: bible.Version = version

        self.tree: ElementTree = ElementTree.parse(
            os.path.join(INPUT_FOLDER, f"{version.value.lower()}.xml"),
        )
        self.namespaces: dict[str, str] = {
            "xmlns": get_namespace(self.tree.getroot().tag),
        }

        self.html: str = ""
        self.html_readers: str = ""
        self.html_notes: str = ""
        self.plain_text: str = ""
        self.plain_text_readers: str = ""
        self.plain_text_notes: str = ""

        self.html_verse_start_indices: dict[int, int] = {}
        self.html_readers_verse_start_indices: dict[int, int] = {}
        self.html_notes_verse_start_indices: dict[int, int] = {}
        self.plain_text_verse_start_indices: dict[int, int] = {}
        self.plain_text_readers_verse_start_indices: dict[int, int] = {}
        self.plain_text_notes_verse_start_indices: dict[int, int] = {}

        self.html_verse_end_indices: dict[int, int] = {}
        self.html_readers_verse_end_indices: dict[int, int] = {}
        self.html_notes_verse_end_indices: dict[int, int] = {}
        self.plain_text_verse_end_indices: dict[int, int] = {}
        self.plain_text_readers_verse_end_indices: dict[int, int] = {}
        self.plain_text_notes_verse_end_indices: dict[int, int] = {}

        self.short_titles: dict[bible.Book, str] = {}
        self.long_titles: dict[bible.Book, str] = {}

    def parse(self: OSISParser) -> None:
        """Parse the XML input file."""
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

            self.html_verse_start_indices.update(book_parser.html_verse_start_indices)
            self.html_readers_verse_start_indices.update(
                book_parser.html_readers_verse_start_indices,
            )
            self.html_notes_verse_start_indices.update(
                book_parser.html_notes_verse_start_indices,
            )
            self.plain_text_verse_start_indices.update(
                book_parser.plain_text_verse_start_indices,
            )
            self.plain_text_readers_verse_start_indices.update(
                book_parser.plain_text_readers_verse_start_indices,
            )
            self.plain_text_notes_verse_start_indices.update(
                book_parser.plain_text_notes_verse_start_indices,
            )

            self.html_verse_end_indices.update(book_parser.html_verse_end_indices)
            self.html_readers_verse_end_indices.update(
                book_parser.html_readers_verse_end_indices,
            )
            self.html_notes_verse_end_indices.update(
                book_parser.html_notes_verse_end_indices,
            )
            self.plain_text_verse_end_indices.update(
                book_parser.plain_text_verse_end_indices,
            )
            self.plain_text_readers_verse_end_indices.update(
                book_parser.plain_text_readers_verse_end_indices,
            )
            self.plain_text_notes_verse_end_indices.update(
                book_parser.plain_text_notes_verse_end_indices,
            )

            self.short_titles[book] = book_parser.short_title
            self.long_titles[book] = book_parser.title

    def write(self: OSISParser) -> None:
        """Write the content out to file(s)."""
        version_str: str = self.version.value.lower()
        version_folder: str = os.path.join(OUTPUT_FOLDER, version_str)

        for folder in (OUTPUT_FOLDER, version_folder):
            if not os.path.exists(folder):
                os.mkdir(folder)

        _write_file(
            version_folder,
            "html.py",
            self.version,
            self.html,
            self.html_verse_start_indices,
            self.html_verse_end_indices,
            True,
        )
        _write_file(
            version_folder,
            "html_readers.py",
            self.version,
            self.html_readers,
            self.html_readers_verse_start_indices,
            self.html_readers_verse_end_indices,
            True,
        )
        _write_file(
            version_folder,
            "html_notes.py",
            self.version,
            self.html_notes,
            self.html_notes_verse_start_indices,
            self.html_notes_verse_end_indices,
            True,
        )
        _write_file(
            version_folder,
            "plain_text.py",
            self.version,
            self.plain_text,
            self.plain_text_verse_start_indices,
            self.plain_text_verse_end_indices,
        )
        _write_file(
            version_folder,
            "plain_text_readers.py",
            self.version,
            self.plain_text_readers,
            self.plain_text_readers_verse_start_indices,
            self.plain_text_readers_verse_end_indices,
        )
        _write_file(
            version_folder,
            "plain_text_notes.py",
            self.version,
            self.plain_text_notes,
            self.plain_text_notes_verse_start_indices,
            self.plain_text_notes_verse_end_indices,
        )

        _write_titles_file(version_folder, self.short_titles, self.long_titles)

    def _get_book_element(self: OSISParser, book: bible.Book) -> Any:
        xpath: str = XPATH_BOOK.format(BOOK_IDS.get(book))
        return self.tree.find(xpath, namespaces=self.namespaces)


def _write_file(
    folder: str,
    filename: str,
    version: bible.Version,
    bible_text: str,
    verse_start_indices: dict[int, int],
    verse_end_indices: dict[int, int],
    is_html: bool = False,
) -> None:
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as writer:
        writer.write(_file_header())
        writer.write("from pythonbible.bible.bible import Bible\n")
        writer.write("from pythonbible.versions import Version\n\n\n")
        writer.write("bible = Bible(\n")
        writer.write(f"    Version.{version.name},\n")
        writer.write(f'    """{bible_text}""",\n')
        writer.write(f"    {verse_start_indices},\n")
        writer.write(f"    {verse_end_indices},\n")
        writer.write(f"    {is_html},\n")
        writer.write(")\n")


def _write_titles_file(
    folder: str, short_titles: dict[bible.Book, str], long_titles: dict[bible.Book, str]
) -> None:
    with open(os.path.join(folder, "titles.py"), "w", encoding="utf-8") as writer:
        writer.write(_file_header())
        writer.write("from pythonbible.books import Book\n\n\n")
        writer.write(f"short_titles = {_titles_dict_to_string(short_titles)}\n\n")
        writer.write(f"long_titles = {_titles_dict_to_string(long_titles)}\n")


def _titles_dict_to_string(titles: dict[bible.Book, str]) -> str:
    return (
        "{\n"
        + ",\n".join(
            [f"    Book.{book.name}: '{title}'" for book, title in titles.items()]
        )
        + ",\n}"
    )


def _file_header() -> str:
    return (
        f"# This file was automatically generated by the pythonbible-parser package "
        f"on {datetime.now()}.\n\n"
    )
