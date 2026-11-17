
import argparse
from pathlib import Path

SYMBOLS = "0123456789ABCDEF"
HEADER_SIZE = 12
RECORD_SIZE = 160


def decode_solution(data):
    """128 bytes -> 256 values (0~15)"""
    values = []

    for byte in data:
        values.append((byte >> 4) & 0xF)
        values.append(byte & 0xF)

    return values


def decode_puzzle(solution, mask):
    """Restore puzzle from solution and clue mask"""
    puzzle = []

    for i in range(256):
        visible = mask[i // 8] & (1 << (7 - (i % 8)))

        if visible:
            puzzle.append(solution[i])
        else:
            puzzle.append(None)

    return puzzle


def print_board(board):
    """Print 16x16 Sudoku with 4x4 box separators"""

    separator = "-" * 41

    for row in range(16):
        if row > 0 and row % 4 == 0:
            print(separator)

        cells = []

        for col in range(16):
            value = board[row * 16 + col]

            if value is None:
                cells.append(".")
            else:
                cells.append(SYMBOLS[value])

        groups = [
            " ".join(cells[i:i + 4])
            for i in range(0, 16, 4)
        ]

        print(" | ".join(groups))


def validate_solution(solution):
    expected = set(range(16))

    for r in range(16):
        row = solution[r * 16:(r + 1) * 16]
        if set(row) != expected:
            return False

    for c in range(16):
        col = [solution[r * 16 + c] for r in range(16)]
        if set(col) != expected:
            return False

    for br in range(0, 16, 4):
        for bc in range(0, 16, 4):
            box = [
                solution[(br + r) * 16 + bc + c]
                for r in range(4)
                for c in range(4)
            ]

            if set(box) != expected:
                return False

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to base16.bin")
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="Puzzle number (starting from 1)"
    )
    args = parser.parse_args()

    data = Path(args.file).read_bytes()

    if len(data) < HEADER_SIZE:
        raise ValueError("File too small")

    payload_size = len(data) - HEADER_SIZE

    if payload_size % RECORD_SIZE != 0:
        raise ValueError(
            f"Invalid file size: {len(data)} bytes"
        )

    count = payload_size // RECORD_SIZE

    if not 1 <= args.index <= count:
        raise ValueError(
            f"Puzzle index must be between 1 and {count}"
        )

    offset = HEADER_SIZE + (args.index - 1) * RECORD_SIZE
    record = data[offset:offset + RECORD_SIZE]

    solution = decode_solution(record[:128])
    mask = record[128:160]

    puzzle = decode_puzzle(solution, mask)

    print(f"File: {args.file}")
    print(f"Header (hex): {data[:HEADER_SIZE].hex()}")
    print(f"Total puzzles: {count}")
    print(f"Puzzle index: {args.index}")
    print(f"Clues: {sum(v is not None for v in puzzle)}")

    print("\n========== PUZZLE ==========\n")
    print_board(puzzle)

    print("\n========== SOLUTION ==========\n")
    print_board(solution)

    print("\n========== VALIDATION ==========")
    print("Solution valid:", validate_solution(solution))


if __name__ == "__main__":
    main()
