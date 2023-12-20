#!/bin/bash

echo Getting transactions using $1. Folder contents:
ls /inout

if [[ "$1" == "sandebit" ]]; then
  poetry run python xls2csv/generateSantanderDebit.py /inout
elif [[ "$1" == "sancredit" ]]; then
  poetry run python xls2csv/generateSantanderCredit.py /inout
fi
