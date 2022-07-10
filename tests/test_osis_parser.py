from functools import lru_cache

import pythonbible as bible

from pythonbible_parser.bible import Bible
from pythonbible_parser.osis.osis_parser import OSISParser


@lru_cache()
def get_parser(version: bible.Version) -> OSISParser:
    parser = OSISParser(version)
    parser.parse()
    return parser


def test_exodus_20_3_asv() -> None:
    """Test for https://github.com/avendesora/pythonbible/issues/9!"""
    # Given the verse id for Exodus 20:3
    verse_id: int = 2020003

    # When we get the verse text using the ASV parser
    version: bible.Version = bible.Version.AMERICAN_STANDARD
    parser: OSISParser = get_parser(version)
    asv_plain: Bible = Bible(
        version,
        parser.plain_text,
        parser.plain_text_verse_start_indeces,
        parser.plain_text_verse_end_indeces,
    )
    verse_text: str = asv_plain.get_scripture(verse_id)

    # Then the verse text is not missing any words.
    assert verse_text == "3. Thou shalt have no other gods before me."


def test_mark_9_38_kjv() -> None:
    """Test for https://github.com/avendesora/pythonbible/issues/12!"""
    # Given the verse id for Mark 9:38
    verse_id: int = 41009038

    # When we get the verse text using the KJV parser
    version: bible.Version = bible.Version.KING_JAMES
    parser: OSISParser = get_parser(version)
    kjv_plain: Bible = Bible(
        version,
        parser.plain_text,
        parser.plain_text_verse_start_indeces,
        parser.plain_text_verse_end_indeces,
    )
    verse_text: str = kjv_plain.get_scripture(verse_id)

    # Then there are no errors and the verse text is as expected
    assert (
        verse_text == "38. And John answered him, saying, Master, we saw one "
        "casting out devils in thy name, and he followeth not us: "
        "and we forbad him, because he followeth not us."
    )


def test_mark_9_43_kjv() -> None:
    """Test for https://github.com/avendesora/pythonbible/issues/16!"""
    # Given the verse id for Mark 9:43
    verse_id: int = 41009043

    # When we get the verse text using the KJV parser
    version: bible.Version = bible.Version.KING_JAMES
    parser: OSISParser = get_parser(version)
    kjv_plain: Bible = Bible(
        version,
        parser.plain_text,
        parser.plain_text_verse_start_indeces,
        parser.plain_text_verse_end_indeces,
    )
    verse_text: str = kjv_plain.get_scripture(verse_id)

    # Then there are no errors and the verse text is as expected
    assert (
        verse_text == "43. And if thy hand offend thee, cut it off: it is "
        "better for thee to enter into life maimed, than having two hands "
        "to go into hell, into the fire that never shall be quenched:"
    )


def test_matthew_17_21_asv() -> None:
    """Test for https://github.com/avendesora/pythonbible/issues/19!"""
    # Given the verse id for Matthew 17:21
    verse_id: int = 40017021

    # When we get the verse text using the ASV parser
    version: bible.Version = bible.Version.AMERICAN_STANDARD
    parser: OSISParser = get_parser(version)
    asv_plain: Bible = Bible(
        version,
        parser.plain_text,
        parser.plain_text_verse_start_indeces,
        parser.plain_text_verse_end_indeces,
    )
    verse_text: str = asv_plain.get_scripture(verse_id)

    # Then there are no errors and the verse text is as expected
    assert verse_text == "21. But this kind goeth not out save by prayer and fasting."


def test_1_chronicles_16_8_kjv() -> None:
    """Test for https://github.com/avendesora/pythonbible/issues/50!"""
    # Given the verse id for 1 Chronicles 16:8
    verse_id: int = 13016008

    # When we get the verse text using the KJV parser
    version: bible.Version = bible.Version.KING_JAMES
    parser: OSISParser = get_parser(version)
    kjv_plain: Bible = Bible(
        version,
        parser.plain_text,
        parser.plain_text_verse_start_indeces,
        parser.plain_text_verse_end_indeces,
    )
    verse_text: str = kjv_plain.get_scripture(verse_id)

    # Then there are no errors and the verse text is as expected
    assert (
        verse_text == "8. Give thanks unto the LORD, call upon his name, make known "
        "his deeds among the people."
    )
