"""Paging and segmentation address translation."""

from collections.abc import Sequence
from typing import Optional


def calculate_paged_address(
    page_size: int, page_table: Sequence[int], logical_address: int
) -> int:
    """Translate a logical address through a page table."""
    if page_size <= 0:
        raise ValueError("page size must be greater than zero")
    if logical_address < 0:
        raise ValueError("logical address cannot be negative")

    page_number, offset = divmod(logical_address, page_size)
    if page_number >= len(page_table):
        raise ValueError(f"page {page_number} is outside the page table")

    frame_number = page_table[page_number]
    if frame_number == -1:
        raise ValueError(f"page {page_number} is unmapped")
    if frame_number < -1:
        raise ValueError(f"page {page_number} has an invalid frame number")

    return frame_number * page_size + offset


def calculate_segmented_address(
    segment_number: int,
    offset: int,
    bases: Sequence[int],
    limits: Sequence[int],
) -> int:
    """Translate a segment reference after checking its limit."""
    if len(bases) != len(limits):
        raise ValueError("base and limit tables must have the same size")
    if segment_number < 0 or segment_number >= len(bases):
        raise ValueError(f"segment {segment_number} is outside the segment table")
    if offset < 0:
        raise ValueError("segment offset cannot be negative")

    base = bases[segment_number]
    if base < 0:
        raise ValueError("segment base cannot be negative")
    limit = limits[segment_number]
    if limit < 0:
        raise ValueError("segment limit cannot be negative")
    if offset >= limit:
        raise ValueError(
            f"offset {offset} exceeds segment {segment_number} limit {limit}"
        )

    return bases[segment_number] + offset


def read_integer(prompt: str, *, minimum: Optional[int] = None) -> int:
    """Read an integer and keep asking until it satisfies the requested bound."""
    while True:
        try:
            value = int(input(prompt))
            if minimum is not None and value < minimum:
                raise ValueError(f"value must be at least {minimum}")
            return value
        except ValueError as error:
            print(f"Invalid input: {error}")


def read_integer_list(prompt: str, expected_count: int) -> list[int]:
    """Read a fixed-length list of integers."""
    while True:
        try:
            values = [int(value) for value in input(prompt).replace(",", " ").split()]
            if len(values) != expected_count:
                raise ValueError(f"enter exactly {expected_count} values")
            return values
        except ValueError as error:
            print(f"Invalid input: {error}")


def paging_demo() -> None:
    print("===== PAGING =====")
    page_size = read_integer("Enter page size: ", minimum=1)
    page_count = read_integer("Enter number of page-table entries: ", minimum=1)
    page_table = read_integer_list(
        "Enter frame numbers (-1 for an unmapped page): ", page_count
    )
    logical_address = read_integer("Enter logical address: ", minimum=0)

    page_number, offset = divmod(logical_address, page_size)
    print(f"Page number = logical address // page size = {logical_address} // {page_size} = {page_number}")
    print(f"Offset = logical address % page size = {logical_address} % {page_size} = {offset}")

    if page_number >= len(page_table):
        print(f"Invalid page: page {page_number} is outside the page table.")
        return

    frame_number = page_table[page_number]
    print(f"Page-table entry[{page_number}] = {frame_number}")
    if frame_number == -1:
        print(f"Invalid page: page {page_number} is unmapped.")
        return
    if frame_number < -1:
        print(f"Invalid page: page {page_number} has an invalid frame number.")
        return

    physical_address = calculate_paged_address(page_size, page_table, logical_address)
    print(f"Physical address = frame number * page size + offset")
    print(f"                  = {frame_number} * {page_size} + {offset} = {physical_address}")


def segmentation_demo() -> None:
    print("\n===== SEGMENTATION =====")
    segment_count = read_integer("Enter number of segments: ", minimum=1)
    bases = read_integer_list("Enter base values: ", segment_count)
    limits = read_integer_list("Enter limit values: ", segment_count)
    segment_number = read_integer("Enter segment number: ", minimum=0)
    offset = read_integer("Enter segment offset: ", minimum=0)

    if segment_number >= segment_count:
        print(f"Invalid segment: segment {segment_number} is outside the segment table.")
        return

    base = bases[segment_number]
    limit = limits[segment_number]
    print(f"Segment-table entry[{segment_number}] = base {base}, limit {limit}")
    print(f"Validity check: 0 <= offset < limit -> 0 <= {offset} < {limit}")
    if base < 0:
        print("Invalid segment reference: the segment base cannot be negative.")
        return
    if limit < 0 or offset >= limit:
        print(f"Invalid segment reference: offset {offset} is outside the segment limit.")
        return

    physical_address = calculate_segmented_address(
        segment_number, offset, bases, limits
    )
    print(f"Physical address = base + offset = {base} + {offset} = {physical_address}")


def main() -> None:
    paging_demo()
    segmentation_demo()


if __name__ == "__main__":
    main()