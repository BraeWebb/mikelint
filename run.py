from typing import Type

from astroid import parse, Module
import argparse
import yaml

from linter.analysers import (
    Analyser,
    ClassInstanceAnalyser,
    DocstringAnalyser,
    EncapsulationAnalyser,
    NamingAnalyser,
    ScopeAnalyser,
    StructureAnalyser
)
from linter.formatters import Formatter, BaseFormatter
from linter.type_hints import AnalyserHelper
from linter.utils.tree import SyntaxTree
from linter.utils.violation import BaseViolation


class Run:
    def __init__(self, analysers: list[Type[Analyser]],
                 formatter: Type[Formatter],
                 source_file_names: list[str], config_file_name: str):
        self._analysers = analysers
        self._formatter_cls = formatter
        self._analyser_helpers: dict[str, AnalyserHelper] = {}
        for source_file_name in source_file_names:
            with open(source_file_name) as fin:
                source = fin.read()
            module: Module = parse(source)
            lines = source.splitlines()
            tree = SyntaxTree(module)
            self._analyser_helpers[source_file_name] = AnalyserHelper(tree,
                                                                      lines)

        with open(config_file_name) as config_file:
            self._config = yaml.load(config_file, Loader=yaml.SafeLoader)
        self._results: dict[str, dict[str, BaseViolation]] = {}
        # Uncomment to see source tree
        # print(module.repr_tree())

    def run(self):
        for analyser_cls in self._analysers:
            analyser = analyser_cls(self._analyser_helpers)
            analyser.run()
            self._results[analyser_cls.__name__] = analyser.get_results()

    def print_results(self):
        formatter = self._formatter_cls(self._config, self._results)
        print(formatter.format())

    def get_results(self):
        return self._results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Configuration file",
                        required=True)
    parser.add_argument("-s", "--source", help="Source file",
                        required=True)
    args = parser.parse_args()
    analysers = [
        ClassInstanceAnalyser,
        DocstringAnalyser,
        EncapsulationAnalyser,
        NamingAnalyser,
        ScopeAnalyser,
        StructureAnalyser
    ]
    runner = Run(analysers, BaseFormatter, args.source, args.config)
    runner.run()
    runner.print_results()


if __name__ == '__main__':
    main()
