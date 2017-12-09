Fully configurable gender ratio map webapp with sub-city detail.

Note: This requires a DB (Postgres by default) to actually run. The scripts for creating the DB are in this repo, but the source data from which the DB is populated is too big to be stored in GitHub.

Start server (from app directory):
`gunicorn --bind 0.0.0.0:8000 application:application -w 1 --threads 12`

Disclaimer: I made this by myself for myself to learn a bit about web apps. Figured other people might find it interesting though.
