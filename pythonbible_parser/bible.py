from functools import lru_cache
from typing import Dict, Optional

from pythonbible import InvalidVerseError, Version, is_valid_verse_id


class Bible:
    def __init__(
        self,
        version: Version,
        content: str,
        verse_start_indices: Dict[int, int],
        verse_end_indices: Dict[int, int],
        is_html: bool = False,
    ):
        self.version: Version = version
        self.content: str = content
        self.verse_start_indices: Dict[int, int] = verse_start_indices
        self.verse_end_indices: Dict[int, int] = verse_end_indices
        self.is_html: bool = is_html

    @lru_cache()
    def get_scripture(self, start_verse_id: int, end_verse_id: Optional[int] = None):
        if not is_valid_verse_id(start_verse_id):
            raise InvalidVerseError(
                f"start verse id ({start_verse_id}) is not a valid verse id."
            )

        if end_verse_id and not is_valid_verse_id(end_verse_id):
            raise InvalidVerseError(
                f"end verse id ({end_verse_id}) is not a valid verse id."
            )

        end_verse_id = end_verse_id or start_verse_id
        start_index = self.verse_start_indices.get(start_verse_id)
        end_index = self.verse_end_indices.get(end_verse_id)

        return self._clean(self.content[start_index:end_index])

    @lru_cache()
    def _clean(self, content: str) -> str:
        cleaned_content: str = content.strip()
        return clean_html(cleaned_content) if self.is_html else cleaned_content


@lru_cache()
def clean_html(content: str) -> str:
    if not content or content in {"</p><p>", "<p></p>"}:
        return ""

    cleaned_content: str = content

    if cleaned_content.endswith("<p>"):
        cleaned_content = cleaned_content[:-3]

    if not cleaned_content.startswith("<p>"):
        cleaned_content = f"<p>{cleaned_content}"

    if not cleaned_content.endswith("</p>"):
        cleaned_content = f"{cleaned_content}</p>"

    return "" if cleaned_content == "<p></p>" else cleaned_content
