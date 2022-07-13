from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pythonbible import Book

from pythonbible_parser.osis.constants import get_book_by_id


@lru_cache()
def get_namespace(tag: str) -> str:
    return tag[tag.index("{") + 1 : tag.index("}")]


@lru_cache()
def strip_namespace_from_tag(tag: str) -> str:
    return tag.replace(get_namespace(tag), "").replace("{", "").replace("}", "")


@lru_cache()
def get_element_text_and_tail(element: Any) -> str:
    return get_element_text(element) + get_element_tail(element)


@lru_cache()
def get_element_text(element: Any) -> str:
    return element.text.replace("\n", " ") if element.text else ""


@lru_cache()
def get_element_tail(element: Any) -> str:
    return element.tail.replace("\n", " ") if element.tail else ""


@dataclass
class OSISID:
    book: Book
    chapter: int
    verse: int


def parse_osis_id(osis_id: str) -> OSISID:
    book_id: str
    chapter: str
    verse: str
    book_id, chapter, verse = osis_id.split(".")

    return OSISID(get_book_by_id(book_id), int(chapter), int(verse))
