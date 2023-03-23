import argparse
import sys
import os
import pypandoc
from .finding_list import FindingList, OUTPUT_FILE_DEFAULT_NAME
from .__version__ import __version__
import logging as log

from dotenv import load_dotenv

load_dotenv()

log.basicConfig(level=log.INFO)

PDF_TEMPLATE = "eisvogel"
EXTRA_ARGS = ["--listings"]


def main():
    parser = argparse.ArgumentParser(
        description="Convert Trello CSV to audit markdown report"
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="Display package version"
    )
    parser.add_argument(
        "csv_file_or_board_id",
        type=str,
        nargs="?",
        help="Input CSV file or URL to trello board. You will need your API key and token. ",
    )
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
    parser.add_argument(
        "-u",
        "--use-attachment-name-for-report",
        default=None,
        help="You can use a specific file name to generate the markdown finding report instead of the description. NOTE: If you use this, you'll need your API key set.",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        default=os.getenv("TRELLO_API_KEY"),
        help="Your Trello API key. You can set this as an environment variable TRELLO_API_KEY",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=os.getenv("TRELLO_API_TOKEN"),
        help="Your Trello API token. You can set this as an environment variable TRELLO_API_TOKEN",
    )
    parser.add_argument(
        "-b",
        "--text-before-file",
        help="A markdown file of text that you'd like to append to the start of the report.",
    )
    parser.add_argument(
        "-p",
        "--pdf-output",
        help="Generate a PDF from the markdown file at this location. You'll need pandoc installed.",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    log.info("Parsing args...")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    log.info("Generating markdown...")
    markdown_findings_list = FindingList(
        csv_file_or_board_id=args.csv_file_or_board_id,
        attachment_name=args.use_attachment_name_for_report,
        api_key=args.api_key,
        token=args.token,
    )

    text_before = ""
    if args.text_before_file:
        log.info("Getting text before...")
        with open(args.text_before_file, "r") as f:
            text_before = f.read()

    if args.dry_run:
        log.info("Dry run, printing to stdout\n")
        print(text_before)
        markdown_findings_list.print_findings_list()
    else:
        log.info(f"Saving to output file: {args.output}")
        markdown_findings_list.save_to_output_file(args.output, text_before)
        if args.pdf_output:
            log.info(f"Generating PDF: {args.pdf_output}")
            pypandoc.convert_file(
                args.output,
                "pdf",
                outputfile=args.pdf_output,
                extra_args=["--template=" + PDF_TEMPLATE] + EXTRA_ARGS,
            )


if __name__ == "__main__":
    main()
