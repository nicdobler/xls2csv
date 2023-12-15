# XLS2CSV

Simple project to convert an XLS to CSV

## Prerequisites
To run this application, you need to have Docker installed on your system.

## Usage
Run the following command in your terminal:

```
make run file=<file>
```
Replace `<file>` with the file to convert.

## Tests
The unit tests for the sign_printer app require `pytest`, which can be installed with `pip`:

```
make test
```

## Linting

To lint the code, run the following command:

```
make lint
```

## Formatting

To format the code, run the following command:

```
make format
```

## pre-commit

### Installation
To enable the pre-commit hook, run the following command:
```
poetry run pre-commit install
```
