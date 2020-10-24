from src.parser.fs_parser import FSParser


def test_parser():
    test_cases = [
        "fsome content",  # content of a file
        "d/mnt\x00dBD\x00fsample.txt\x00dRC",  # directory + children
        "d/usr/bin/env\x00",  # empty directory
        "f"  # empty file
    ]

    for test_case in test_cases:
        result = FSParser.parse(test_case)
        print(result)


if __name__ == "__main__":
    test_parser()
