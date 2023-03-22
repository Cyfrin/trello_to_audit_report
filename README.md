# Trello To Audit Report

A way to easily generate a markdown file from a trello board.

# Getting Started

## Requirements

## Requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
  - You'll know you did it right if you can run `git --version` and you see a response like `git version x.x.x`
- [Python](https://www.python.org/downloads/)
  - You'll know you've installed python right if you can run:
    - `python --version` or `python3 --version` and get an output like: `Python x.x.x`
- [pipx](https://pypa.github.io/pipx/installation/)
  - `pipx` is different from [pip](https://pypi.org/project/pip/)
  - You may have to close and re-open your terminal
  - You'll know you've installed it right if you can run:
    - `pipx --version` and see something like `x.x.x.x`

## Quickstart

1. Download and install this package with `pip` or `pipx`

```
pipx install trello_to_audit_report
```

You can run `trello_to_audit_report -v` to make sure it's installed correctly.

2. Place all your findings in a list on a trello board, and have one list called `Report`
3. [Export your board](https://support.atlassian.com/trello/docs/exporting-data-from-trello/) to a `.csv` file
4. Run:

```
trello_to_audit_report <PATH_TO_YOUR_CSV>
```

And you'll get a file named `output.md` with all your code formatted!

# More Resources

You can then, dump it into `pandoc` to generate a PDF. We have [a repo](https://github.com/ChainAccelOrg/audit-report-templating) that shows you how to do that as well. 
