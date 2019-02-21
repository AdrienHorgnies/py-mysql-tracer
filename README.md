# mysql_tracer
A MySQL client to run queries, write execution reports and export results.

It is made with the purpose to support SELECT statements only.
Other statements will work but the features offered by this module will provide little help or make no sense.

## Usage

This can be used as a command line tool:
```
$ mysql_tracer -h
usage: mysql_tracer [-h] --host HOST --user USER [--database DATABASE] [-a]
                    [-s] [-d DESTINATION | --display]
                    query [query ...]

positional arguments:
  query                 Path to a file containing a single sql statement

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           MySQL server host
  --user USER           MySQL server user
  --database DATABASE   MySQL database name
  -a, --ask-password    Do not try to retrieve password from keyring, always
                        ask password
  -s, --store_password  Store password into keyring after connecting to the
                        database
  -d DESTINATION, --destination DESTINATION
                        Directory where to export results
  --display             Do not export results but display them to stdout

```

It exposes the class `Query`. The constructor needs a path to a file containing a single sql statement and instances 
expose the method `export` which creates a timestamped copy of the original file, appended with an execution report and
an export of the result in the csv format. 

## Development

You can install dependencies with `pip install -r requirements.txt`.

You can run tests with `pytest` but you need to set `PYTHONPATH`.
```
$ export PYTHONPATH=mysql_tracer
$ python3 -m pytest
```

Or you can setup a test run with your IDE without any particular configuration.
