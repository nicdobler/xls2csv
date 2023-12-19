#!/bin/bash

#if [ "$1" = "sandebit" ]; then
  poetry run python xls2csv/generateSantanderDebit.py /inout/$2
#else if [ "$1" = "sancredit" ]; then
#  poetry run python xls2csv/generateSantanderCredit.py /inout/$2
#else if [ "$1" = "folderCombine" ]; then
#  poetry run python xls2csv/xls2csv.py /inout
#else
#  exit 1 "Command not supported. Usage: run <sanDebit|sanCredit|folderCombine>"
#fi