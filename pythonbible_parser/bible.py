from typing import Dict, Optional

from pythonbible import InvalidVerseError, Version, is_valid_verse_id


class Bible:
    def __init__(
        self,
        version: Version,
        content: str,
        verse_start_indices: Dict[int, int],
        verse_end_indices: Dict[int, int],
    ):
        self.version: Version = version
        self.content: str = content
        self.verse_start_indices: Dict[int, int] = verse_start_indices
        self.verse_end_indices: Dict[int, int] = verse_end_indices

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

        return self.content[start_index:end_index].strip()
