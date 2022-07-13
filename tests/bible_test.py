from __future__ import annotations

import pytest
from pythonbible import InvalidVerseError, Version

from pythonbible_parser.bible import Bible


def test_invalid_start_verse() -> None:
    # Given an invalid start verse id and a Bible instance
    start_verse_id = 99999999
    bible = Bible(Version.KING_JAMES, "content", {1: 1}, {1: 1})

    # When getting the scripture text for that verse
    # Then an InvalidVerseError is raised.
    with pytest.raises(InvalidVerseError):
        bible.get_scripture(start_verse_id)


def test_invalid_end_verse() -> None:
    # Given an valid start verse id, an invalid end verse id, and a Bible instance
    start_verse_id = 1001001
    end_verse_id = 99999999
    bible = Bible(Version.KING_JAMES, "content", {1: 1}, {1: 1})

    # When getting the scripture text for that verse
    # Then an InvalidVerseError is raised.
    with pytest.raises(InvalidVerseError):
        bible.get_scripture(start_verse_id, end_verse_id)


def test_start_verse_none() -> None:
    # Given an null start verse id and a Bible instance
    start_verse_id = None
    bible = Bible(Version.KING_JAMES, "content", {1: 1}, {1: 1})

    # When getting the scripture text for that verse
    # Then an InvalidVerseError is raised.
    with pytest.raises(InvalidVerseError):
        bible.get_scripture(start_verse_id)
