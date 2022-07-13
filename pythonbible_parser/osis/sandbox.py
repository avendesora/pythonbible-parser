from __future__ import annotations

from logging import info

number_of_characters: int = 0
tags: set[str] = set()
current_tag: str = ""
in_tag: bool = False

with open("versions/asv.xml", "r", encoding="utf-8") as reader:
    while True:
        character: str = reader.read(1)

        if not character:
            if current_tag:
                tags.add(current_tag)
                current_tag = ""
                in_tag = False
            break

        if current_tag and (not character.strip() or character in {">", "/"}):
            tags.add(current_tag)
            current_tag = ""
            in_tag = False
            continue

        if character == "<":
            in_tag = True
            continue

        if in_tag and character != "/":
            current_tag += character

        number_of_characters += 1

    info(f"Total number of characters = {number_of_characters}.")

    sorted_tags = sorted(tags)
    for tag in sorted_tags:
        info(tag)
