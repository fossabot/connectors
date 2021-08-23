# Metaphor Connectors

[![CI/CD](https://github.com/MetaphorData/connectors/actions/workflows/cicd.yml/badge.svg)](https://github.com/MetaphorData/connectors/actions/workflows/cicd.yml)
[![PyPI Version](https://img.shields.io/pypi/v/metaphor-connectors)](https://pypi.org/project/metaphor-connectors/)
![Python version 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/github/license/MetaphorData/connectors)](https://github.com/MetaphorData/connectors/blob/master/LICENSE)

This repository contains a collection of Python-based "connectors" that extract metadata from various sources to ingest into the Metaphor app.

Each connector is placed under its own directory under `metaphor` and is expected to extend `metaphor.common.BaseExtractor`.

## Installation

This package requires Python 3.7+ installed. You can verify the version on your system by running the following command,

```shell
python -V  # or python3 -V on some systems
```

Once verified, you can install the package using [pip](https://docs.python.org/3/installing/index.html),

```shell
pip install metaphor-connectors[all]
```

This will install all the connectors and required dependencies. You can also choose to install only a subset of the dependencies by installing specific [extra](https://packaging.python.org/tutorials/installing-packages/#installing-setuptools-extras), e.g.

```shell
pip install metaphor-connectors[snowflake]
```

Similary, you can also install the package using `requirements.txt` or `pyproject.toml`.

## Development

See [Development Environment](docs/develop.md) for more instructions on how to setup your local development environment.
