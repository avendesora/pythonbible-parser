# from __future__ import annotations
#
# from logging import info
#
# import pythonbible as bible
#
# from pythonbible_parser.formatter import format_scripture_text_with_parser
# from pythonbible_parser.osis.old_osis_parser import OldOSISParser
#
#
# def profile_books() -> None:
#     for book in bible.Book:
#         profile_book(book)
#
#
# def profile_book(book: bible.Book) -> None:
#     info(book)
#
#     info("--> get references")
#     references = bible.get_references(book.title)
#
#     info("--> convert to verse ids")
#     verse_ids = bible.convert_references_to_verse_ids(references)
#
#     info("--> convert back to references")
#     bible.convert_verse_ids_to_references(verse_ids)
#
#     info("--> format reference strings")
#     bible.format_scripture_references(references)
#
#     info("--> format verse text")
#     profile_format_scripture_text(book)
#
#     info("--> get unformatted verse text")
#     bible.format_scripture_text(verse_ids, one_verse_per_paragraph=True)
#
#
# def profile_format_scripture_text(book: bible.Book) -> None:
#     for chapter in range(1, bible.get_number_of_chapters(book) + 1):
#         reference_string = f"{book.title} {chapter}"
#         info(f"--> --> {reference_string}")
#         references = bible.get_references(reference_string)
#         verse_ids = bible.convert_references_to_verse_ids(references)
#         format_scripture_text_with_parser(
#             verse_ids, OldOSISParser(bible.versions.DEFAULT_VERSION)
#         )
#
#
# # % scalene tests/profiler_test.py
# # if __name__ == "__main__":
# #     # profile_books()
# #     profile_book(bible.Book.JAMES)
