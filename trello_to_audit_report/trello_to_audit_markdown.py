import argparse
import sys
from .finding_list import FindingList, OUTPUT_FILE_DEFAULT_NAME

from .__version__ import __version__
from typing import List
from .finding import Finding
import logging as log

log.basicConfig(level=log.INFO)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Trello CSV to audit markdown report"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Display package version"
    )
    parser.add_argument("csv_file", type=str, nargs="?", help="Input CSV file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=OUTPUT_FILE_DEFAULT_NAME,
        help="Output markdown file (default: result.md)",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        default=False,
        action="store_true",
        help="Don't print to output",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    markdown_findings_list = FindingList(args.csv_file)

    if args.dry_run:
        log.info("Dry run, printing to stdout\n")
        markdown_findings_list.print_findings_list()
    else:
        log.info(f"Saving to output file: {args.output}")
        markdown_findings_list.save_to_output_file(args.output)


if __name__ == "__main__":
    main()
