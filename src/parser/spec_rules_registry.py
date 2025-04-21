
from src.parser.spec_rules import (
    SizeSpecParser,
    WeightSpecParser,
    CapacitySpecParser,
    FeatureSpecParser,
    VoltageSpecParser,
    DescriptionSpecParser,
    ColorSpecParser,
    InnerVolumeSpecParser,
    InsulationSpecParser,
    MaterialSpecParser,
    TemperatureRangeSpecParser,
    UsageSpecParser,
    DescriptionBooleanSpecParser,
)
class SpecRuleRegistry:
    def __init__(self, sub_category: str):
        self.parsers = [
            SizeSpecParser(),
            WeightSpecParser(),
            CapacitySpecParser(),
            FeatureSpecParser(),
            VoltageSpecParser(),
            DescriptionBooleanSpecParser(sub_category=sub_category), 
            DescriptionSpecParser(),
            ColorSpecParser(),
            InnerVolumeSpecParser(),
            InsulationSpecParser(),
            MaterialSpecParser(),
            TemperatureRangeSpecParser(),
            UsageSpecParser(),
        ]

    def parse_fragment(self, fragment: str) -> list[tuple[str, str]] | None:
        results = []

        for parser in self.parsers:
            if parser.match(fragment):
                parsed = parser.parse(fragment)
                if isinstance(parsed, list):
                    results.extend(parsed)
                elif parsed:
                    results.append(parsed)

                if isinstance(parser, DescriptionBooleanSpecParser) or isinstance(parser, DescriptionSpecParser):
                    continue
                break 

        return results if results else None
