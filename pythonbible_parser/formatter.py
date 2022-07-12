from typing import Any, Callable, List, Optional

from pythonbible_parser.bible_parser import BibleParser


def format_scripture_text_with_parser(
    verse_ids: List[int],
    parser: BibleParser,
    full_title: bool = False,
    format_type: str = "html",
    include_verse_numbers: bool = True,
) -> str:
    title_function: Callable[[Any], Any] = (
        parser.get_book_title if full_title else parser.get_short_book_title
    )
    text: str = ""

    paragraphs: Any = parser.get_scripture_passage_text(
        verse_ids, include_verse_number=include_verse_numbers
    )

    for book, chapters in paragraphs.items():
        title: str = title_function(book)
        text += _format_title(title, format_type, len(text) == 0)

        for chapter, paragraphs in chapters.items():
            text += _format_chapter(chapter, format_type)

            for paragraph in paragraphs:
                text += _format_paragraph(paragraph, format_type)

    return text


def _format_title(title: str, format_type: str, is_first_book: bool) -> str:
    if format_type == "html":
        return f"<h1>{title}</h1>\n"

    return f"{title}\n\n" if is_first_book else f"\n\n{title}\n\n"


def _format_chapter(chapter: int, format_type: str) -> str:
    if format_type == "html":
        return f"<h2>Chapter {chapter}</h2>\n"

    return f"Chapter {chapter}\n\n"


def _format_paragraph(paragraph: Optional[str], format_type: str) -> str:
    if format_type == "html":
        return f"<p>{paragraph}</p>\n"

    return f"   {paragraph}\n"
