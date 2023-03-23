To get started contributing to this project, you'll first need to set up your development environment.

```
git clone https://github.com/chainaccelorg/trello_to_audit_report
cd trello_to_audit_report

python3 -m venv venv
source venv/bin/activate
```

We set up a virtual environment so that packages you install get installed to an isolated location (the `venv` folder we just created). If you want to exit this virtual environment, you can run `deactivate`.

Then, install the development dependencies.

```
pip install -r requirements.txt
```

### Optional

You can also install the package in editable mode.

```
pip install -e .
```

The `pip install -e .` command installs our package in "editable" mode. This means that any changes you make to the code will be reflected in the package you import in your own code.

This would be if you want to run make changes and test them out on your own code in another project. 


# Tests

## Unit Tests

```bash
pytest
```

## Integration Tests

You'll need a `TRELLO_API_KEY` and `TRELLO_API_TOKEN` environment variables. 

```bash
pytest -m integration
```

## All tests

You'll need a `TRELLO_API_KEY` and `TRELLO_API_TOKEN` environment variables. 

```
pytest -m ""
```

# Uploading to PyPI 

_For maintainers only. You can view the [docs](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives) to learn more._ 

_Note: `setup.py sdist` is deprecated. Use `python3 -m build` instead._

```
python3 -m build
python3 -m twine upload dist/*
```

Right now, we have our GitHub actions setup so that every release we push we automatically upload to PyPI.
