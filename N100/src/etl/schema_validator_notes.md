# DQ implementation notes

DQ-01 through DQ-16 are implemented in `validator.py`. CRITICAL orphan/duplicate/key-format problems are resolved before SQLite insertion; WARNING and INFO findings are retained in `output/validation_failures.csv` for analyst review.
