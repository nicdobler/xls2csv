# XLS2CSV

XLS2CSV is a powerful and flexible tool designed to streamline the process of converting bank statements from XLS or CSV formats into a unified Quicken-ready CSV file. This script intelligently handles statements from multiple banks, merges the data, and removes duplicate transactions by maintaining a local transaction history.

## Supported Banks

The script is designed to parse and process statements from the following banks:

- ING Direct
- Revolut
- Santander (including standard and mobile-generated formats)
- Wise

## Output Format

The script generates a CSV file designed for import into Quicken. The format follows the specification outlined in the [official Quicken CSV documentation](https://info.quicken.com/win/import-transactions-from-csv-file).

## How It Works

The script follows a straightforward workflow to process your bank statements:

1.  **Scans for Files**: It recursively scans the input directory for any supported XLS or CSV bank statements.
2.  **Merges Data**: All transactions from the found files are merged into a single dataset.
3.  **Removes Duplicates**: It removes duplicate entries from the merged data.
4.  **Filters Old Transactions**: A local SQLite database (`database.db`) is used to keep track of processed transactions. The script filters out any transactions that have already been saved.
5.  **Generates CSV**: A new, clean CSV file named `AccountQuickenExport-YYYYMMDD-HHMM.csv` is generated in the input directory, ready for import into Quicken or other financial software.
6.  **Updates Database**: The new transactions are saved to the database to prevent them from being processed again in future runs.
7.  **Archives Processed Files**: The original XLS/CSV files are moved to a `processed` sub-folder within the input directory to keep things tidy.

## Prerequisites
To run this application, you need to have Docker installed on your system.

## Usage

### With Docker (Recommended)

1.  **Place your files**: Put all your XLS and CSV bank statements into a directory on your local machine. The default directory is `~/Downloads/Banks`. If you wish to use a different directory, you will need to update the path in the `Makefile`.

2.  **Run the script**: Execute the following command in your terminal:
    ```sh
    make run
    ```

The script will process all supported files in the `~/Downloads/Banks` directory. The output CSV file (`AccountQuickenExport-*.csv`), the transaction database (`database.db`), and a new `processed` folder containing the original source files will be created inside this same directory.

### Locally (for Development)

1.  **Install dependencies**:
    ```sh
    pip install poetry
    poetry install
    ```

2.  **Run the script**:
    ```sh
    make runLocal
    ```
This command is configured to use `~/Downloads/Banks` as the input/output directory. You can modify the `runLocal` command in the `Makefile` to point to a different path.

## For Developers

### Running Tests

To run the unit tests, execute:

```sh
make test
```

### Linting

To check the code for style issues, run:

```sh
make lint
```

### Formatting

To automatically format the code, run:

```sh
make format
```

### Pre-Commit Hook

To enable the pre-commit hook for automated checks before each commit, run:

```sh
poetry run pre-commit install
```
