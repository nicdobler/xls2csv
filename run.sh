#!/bin/bash

echo Getting transactions using $1.

if [[ "$1" == "debit" ]]; then
  poetry run python xls2csv/generateSantanderDebit.py /inout
elif [[ "$1" == "credit" ]]; then
  poetry run python xls2csv/generateSantanderCredit.py /inout
fi
