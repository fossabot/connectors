<img src="./logo.png" width="300" />

# Metaphor Connectors

[![CI](https://github.com/MetaphorData/connectors/actions/workflows/ci.yml/badge.svg)](https://github.com/MetaphorData/connectors/actions/workflows/ci.yml)
[![CodeQL](https://github.com/MetaphorData/connectors/workflows/CodeQL/badge.svg)](https://github.com/MetaphorData/connectors/actions/workflows/codeql-analysis.yml)
[![PyPI Version](https://img.shields.io/pypi/v/metaphor-connectors)](https://pypi.org/project/metaphor-connectors/)
![Python version 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/MetaphorData/connectors.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/MetaphorData/connectors/context:python)
[![License](https://img.shields.io/github/license/MetaphorData/connectors)](https://github.com/MetaphorData/connectors/blob/master/LICENSE)

This repository contains a collection of Python-based "connectors" that extract metadata from various sources to ingest into the [Metaphor](https://metaphor.io) platform.

## Installation

This package requires Python 3.7+ installed. You can verify the version on your system by running the following command,

```shell
python -V  # or python3 on some systems
```

Once verified, you can install the package using [pip](https://docs.python.org/3/installing/index.html),

```shell
pip install "metaphor-connectors[all]"  # or pip3 on some systems
```

This will install all the connectors and required dependencies. You can also choose to install only a subset of the dependencies by installing the specific [extra](https://packaging.python.org/tutorials/installing-packages/#installing-setuptools-extras), e.g.

```shell
pip install "metaphor-connectors[snowflake]"
```

Similarly, you can also install the package using `requirements.txt` or `pyproject.toml`.

## Connectors

Each connector is placed under its own directory under [metaphor](./metaphor) and extends the `metaphor.common.BaseExtractor` class.

| Connector Name                                               | Metadata                                 |
|--------------------------------------------------------------|------------------------------------------|  
| [airflow_plugin](metaphor/airflow_plugin/README.md)          | Lineage                                  |
| [bigquery](metaphor/bigquery/README.md)                      | Schema, description, statistics          |
| [bigquery.lineage](metaphor/bigquery/lineage/README.md)      | Lineage                                  |
| [bigquery.profile](metaphor/bigquery/profile/README.md)      | Data profile                             |
| [bigquery.query](metaphor/bigquery/query/README.md)          | Queries                                  |
| [bigquery.usage](metaphor/bigquery/usage/README.md)          | Data usage                               |
| [dbt](metaphor/dbt/README.md)                                | dbt model, test, lineage                 |
| [dbt.cloud](metaphor/dbt/cloud/README.md)                    | dbt model, test, lineage                 |
| [glue](metaphor/glue/README.md)                              | Schema, description                      |
| [looker](metaphor/looker/README.md)                          | Looker view, explore, dashboard, lineage |
| [manual.metadata](metaphor/manual/metadata/README.md)        | Custom metadata                          |
| [manual.governance](metaphor/manual/governance/README.md)    | Ownership, tags                          |
| [manual.lineage](metaphor/manual/lineage/README.md)          | Lineage                                  |
| [metabase](metaphor/metabase/README.md)                      | Dashboard, lineage                       |
| [postgresql](metaphor/postgresql/README.md)                  | Schema, description, statistics          |
| [postgresql.profile](metaphor/postgresql/profile/README.md)  | Data profile                             |
| [postgresql.usage](metaphor/postgresql/usage/README.md)      | Usage                                    |
| [power_bi](metaphor/power_bi/README.md)                      | Dashboard, lineage                       |
| [redshift](metaphor/redshift/README.md)                      | Schema, description, statistics          |
| [redshift.lineage](metaphor/redshift/lineage/README.md)      | Lineage                                  |
| [redshift.profile](metaphor/redshift/profile/README.md)      | Data profile                             |
| [redshift.query](metaphor/redshift/query/README.md)          | Queries                                  |
| [redshift.usage](metaphor/redshift/usage/README.md)          | Usage                                    |
| [snowflake](metaphor/snowflake/README.md)                    | Schema, description, statistics          |
| [snowflake.lineage](metaphor/snowflake/lineage/README.md)    | Lineage                                  |
| [snowflake.profile](metaphor/snowflake/profile/README.md)    | Data profile                             |
| [snowflake.query](metaphor/snowflake/query/README.md)        | Queries                                  |
| [snowflake.usage](metaphor/snowflake/usage/README.md)        | Data usage                               |
| [tableau](metaphor/tableau/README.md)                        | Dashboard, lineage                       |
| [unity_catalog](metaphor/unity_catalog/README.md)            | Schema, description                      |

## Development

See [Development Environment](docs/develop.md) for more instructions on how to setup your local development environment.
