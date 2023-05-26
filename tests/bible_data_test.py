from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import pythonbible as pb

from pythonbible_parser.osis.osis_parser import OSISParser

CURRENT_FOLDER: str = Path(os.path.realpath(__file__)).parent
DATA_FOLDER: str = Path(CURRENT_FOLDER / "data")
OUTPUT_FOLDER: str = Path(CURRENT_FOLDER / "output")


def _import_bible_data(file_name: str) -> dict[int, str]:
    bible_data = {}

    with Path(DATA_FOLDER / file_name).open() as json_file:
        json_data = json.load(json_file)
        result_set = json_data["resultset"]
        row = result_set["row"]

        for element in row:
            verse_id, _, _, _, text = element["field"]
            bible_data[verse_id] = text

    return bible_data


KJV_BASELINE = _import_bible_data("t_kjv.json")


@pytest.mark.xfail(reason="The KJV test data seems to be from a slightly different version.")
def test_kjv_bible_data() -> None:
    parser = OSISParser(pb.Version.KING_JAMES)
    parser.parse()

    differences_actual = {}
    differences_expected = {}

    valid: bool = True

    for verse_id in parser.plain_text_readers_verse_start_indices:
        expected = KJV_BASELINE.get(verse_id, "").strip()
        start = parser.plain_text_readers_verse_start_indices[verse_id]
        end = parser.plain_text_readers_verse_end_indices[verse_id]
        actual = parser.plain_text_readers[start:end].replace("`", "'").strip()

        if actual != expected:
            differences_actual[verse_id] = actual
            differences_expected[verse_id] = expected

            valid = False

    if not valid:
        output_folder_path = Path(OUTPUT_FOLDER)

        if not output_folder_path.exists():
            output_folder_path.mkdir()

        actual_file_path = Path(output_folder_path / "kjv_actual.txt")

        with actual_file_path.open(mode="w", encoding="utf-8") as actual_file:
            actual_file.write(str(differences_actual))

        expected_file_path = Path(output_folder_path / "kjv_expected.txt")

        with expected_file_path.open(mode="w", encoding="utf-8") as expected_file:
            expected_file.write(str(differences_expected))

    assert valid
