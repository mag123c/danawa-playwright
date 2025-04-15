
from src.parser.spec_rules import SizeSpecParser
from src.parser.spec_rules import WeightSpecParser
from src.parser.spec_rules import CapacitySpecParser
from src.parser.spec_rules import FeatureSpecParser
from src.parser.spec_rules import VoltageSpecParser
from src.parser.spec_rules import DescriptionSpecParser


class SpecRuleRegistry:
    def __init__(self):
        self.parsers = [
            SizeSpecParser(),
            WeightSpecParser(),
            CapacitySpecParser(),
            FeatureSpecParser(),
            VoltageSpecParser(),
            DescriptionSpecParser(),
        ]

    def parse_fragment(self, fragment: str) -> tuple[str, str] | None:
        for parser in self.parsers:
            if parser.match(fragment):
                return parser.parse(fragment)
        return None
