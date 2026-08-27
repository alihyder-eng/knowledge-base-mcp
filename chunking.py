from __future__ import annotations

import re
from dataclasses import dataclass


def _approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


@dataclass
class Chunk:
    text: str
    chunk_index: int
    char_start: int
    char_end: int


def split_into_paragraphs(text: str) -> list[str]:
    text = text.replace("\r\n", "\n")

    paragraphs = re.split(
        r"\n\s*\n",
        text,
    )

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences while keeping normal punctuation.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def chunk_text(
    text: str,
    chunk_size_tokens: int,
    overlap_tokens: int,
) -> list[Chunk]:

    paragraphs = split_into_paragraphs(text)

    chunks: list[Chunk] = []

    current_sentences: list[str] = []
    current_tokens = 0

    char_cursor = 0
    chunk_start_char = 0

    def flush() -> None:
        nonlocal current_sentences
        nonlocal current_tokens
        nonlocal chunk_start_char

        if not current_sentences:
            return

        chunk_body = " ".join(
            current_sentences
        ).strip()

        if not chunk_body:
            return

        chunks.append(
            Chunk(
                text=chunk_body,
                chunk_index=len(chunks),
                char_start=chunk_start_char,
                char_end=(
                    chunk_start_char
                    + len(chunk_body)
                ),
            )
        )

        current_sentences = []
        current_tokens = 0

    for paragraph in paragraphs:

        sentences = split_into_sentences(
            paragraph
        )

        for sentence in sentences:

            sentence_tokens = _approx_tokens(
                sentence
            )

            # -------------------------------------------------
            # If one sentence is larger than the chunk size,
            # split that sentence by words.
            # -------------------------------------------------

            if sentence_tokens > chunk_size_tokens:

                if current_sentences:
                    flush()

                words = sentence.split()

                words_per_chunk = max(
                    1,
                    chunk_size_tokens * 4 // 5,
                )

                overlap_words = max(
                    0,
                    overlap_tokens * 4 // 5,
                )

                step = max(
                    1,
                    words_per_chunk - overlap_words,
                )

                for start in range(
                    0,
                    len(words),
                    step,
                ):

                    sub_words = words[
                        start:start + words_per_chunk
                    ]

                    if not sub_words:
                        continue

                    sub_text = " ".join(
                        sub_words
                    )

                    chunks.append(
                        Chunk(
                            text=sub_text,
                            chunk_index=len(chunks),
                            char_start=char_cursor,
                            char_end=(
                                char_cursor
                                + len(sub_text)
                            ),
                        )
                    )

                char_cursor += len(sentence) + 1
                chunk_start_char = char_cursor

                continue

            # -------------------------------------------------
            # Add sentence to current chunk if it fits.
            # -------------------------------------------------

            if (
                current_sentences
                and
                current_tokens + sentence_tokens
                > chunk_size_tokens
            ):

                flush()

                # Keep a small sentence overlap.
                overlap_sentences: list[str] = []
                overlap_count = 0

                for previous in reversed(
                    current_sentences
                ):

                    previous_tokens = (
                        _approx_tokens(previous)
                    )

                    if (
                        overlap_count
                        + previous_tokens
                        > overlap_tokens
                    ):
                        break

                    overlap_sentences.insert(
                        0,
                        previous,
                    )

                    overlap_count += (
                        previous_tokens
                    )

                current_sentences = (
                    overlap_sentences
                )

                current_tokens = sum(
                    _approx_tokens(sentence)
                    for sentence
                    in current_sentences
                )

            current_sentences.append(
                sentence
            )

            current_tokens += sentence_tokens

            char_cursor += len(sentence) + 1

        # Finish each paragraph.
        if current_sentences:
            flush()

        char_cursor += 1
        chunk_start_char = char_cursor

    flush()

    return [
        chunk
        for chunk in chunks
        if chunk.text.strip()
    ]