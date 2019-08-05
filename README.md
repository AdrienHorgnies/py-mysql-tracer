# mysql_tracer
A MySQL client to run queries, write execution reports and export results.

It is made with the purpose to support SELECT statements only.
Other statements will work but the features offered by this module will provide little help or make no sense.

It uses Python 3.

## Installing

Package is available on PyPi:

    pip install mysql_tracer

## Usage

This package defines a command line tool named `mst`.
To get help about how to use it: `mst -h`

It exposes the class `Query`. The constructor needs a path to a file containing a single sql statement and instances 
expose the method `export` which creates a timestamped copy of the original file with additional metadata and
the results exported in the CSV format.

## Development

You can install development dependencies with `pip install -r requirements.txt`.

You can run tests with `pytest`.

    pytest

You can run the module from sources by running the whole package:

    python mysql_tracer -h

You can build a package with setuptools.

    python setup.py sdist bdist_wheel

All dependencies have their version frozen.
To install new versions of the dependencies, uninstall them, install the billing-check package and then freeze them again

    pip freeze | xars pip uninstall -y
    python setup.py sdist
    pip install -e .[dev]
    pip freeze | grep -v billing-check > requirements.txt
