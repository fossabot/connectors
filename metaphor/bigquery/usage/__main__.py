from metaphor.common.cli import cli_main

from .extractor import BigQueryUsageExtractor

if __name__ == "__main__":
    cli_main("BigQuery usage metadata extractor", BigQueryUsageExtractor)
