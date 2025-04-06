import re
import random
from itertools import product


class RegexCombinationGenerator:
    def __init__(self, max_repeat=5):
        self.max_repeat = max_repeat
        self.processing_steps = []

    def tokenize(self, regex_str):
        """Split the regex into tokens for parsing."""
        self.processing_steps.append(f"Tokenizing regex: {regex_str}")

        pattern = r'([A-Za-z0-9])|(\()|(\))|(\|)|(\?)|(\*)|(\^)|(\([\+]\))'
        tokens = []

        i = 0
        while i < len(regex_str):
            match = re.match(pattern, regex_str[i:])
            if match:
                if match.group(8):
                    tokens.append("^(+)")
                    i += 3
                elif match.group(7):
                    if i + 1 < len(regex_str) and regex_str[i + 1] == '(':
                        end_paren = regex_str.find(')', i + 2)
                        if end_paren != -1:
                            power = regex_str[i + 2:end_paren]
                            tokens.append(f"^({power})")
                            i = end_paren + 1
                        else:
                            tokens.append(regex_str[i])
                            i += 1
                    else:
                        tokens.append(regex_str[i])
                        i += 1
                else:
                    tokens.append(regex_str[i])
                    i += 1
            else:
                tokens.append(regex_str[i])
                i += 1

        self.processing_steps.append(f"Tokens: {tokens}")
        return tokens

    def parse(self, tokens):
        """Parse tokens into a structured representation."""
        self.processing_steps.append("Starting to parse tokens")

        def parse_group():
            nonlocal i
            i += 1

            options = [[]]
            current_option = 0

            while i < len(tokens) and tokens[i] != ')':
                if tokens[i] == '|':
                    options.append([])
                    current_option += 1
                    i += 1
                else:
                    options[current_option].append(tokens[i])
                    i += 1

            i += 1
            return {'type': 'group', 'options': options}

        result = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token == '(':
                group = parse_group()
                result.append(group)
            elif token == '?':
                if result:
                    prev = result.pop()
                    result.append({'type': 'optional', 'element': prev})
                i += 1
            elif token == '*':
                if result:
                    prev = result.pop()
                    result.append({'type': 'star', 'element': prev})
                i += 1
            elif token.startswith('^'):
                if result and token[1:] == "(+)":
                    prev = result.pop()
                    result.append({'type': 'one_or_more', 'element': prev})
                elif result:
                    power = int(token[2:-1])
                    prev = result.pop()
                    result.append({'type': 'power', 'element': prev, 'power': power})
                i += 1
            else:
                result.append({'type': 'char', 'value': token})
                i += 1

        self.processing_steps.append(f"Parsed structure: {result}")
        return result

    def generate_combinations(self, parsed_regex, max_results=10):
        """Generate combinations based on the parsed regex."""
        self.processing_steps.append("Starting to generate combinations")

        def expand_element(element):
            if element['type'] == 'char':
                return [[element['value']]]

            elif element['type'] == 'group':
                options = []
                for option in element['options']:
                    option_combinations = [[]]
                    for item in option:
                        item_combinations = expand_element({'type': 'char', 'value': item})
                        new_combinations = []
                        for combo in option_combinations:
                            for item_combo in item_combinations:
                                new_combinations.append(combo + item_combo)
                        option_combinations = new_combinations
                    options.extend(option_combinations)
                return options

            elif element['type'] == 'optional':
                inner_combinations = expand_element(element['element'])
                return [[], *inner_combinations]

            elif element['type'] == 'star':
                inner_combinations = expand_element(element['element'])
                results = [[]]

                for repeat_count in range(1, self.max_repeat + 1):
                    for inner_combo in inner_combinations:
                        repeated = inner_combo * repeat_count
                        results.append(repeated)

                return results

            elif element['type'] == 'one_or_more':
                inner_combinations = expand_element(element['element'])
                results = []

                for repeat_count in range(1, self.max_repeat + 1):
                    for inner_combo in inner_combinations:
                        repeated = inner_combo * repeat_count
                        results.append(repeated)

                return results

            elif element['type'] == 'power':
                inner_combinations = expand_element(element['element'])
                results = []
                power = element['power']

                if power == 0:
                    return [[]]

                for inner_combo in inner_combinations:
                    repeated = inner_combo * power
                    results.append(repeated)

                return results

        all_element_combinations = []
        for element in parsed_regex:
            element_combinations = expand_element(element)
            all_element_combinations.append(element_combinations)

        result_combinations = [[]]
        for element_combinations in all_element_combinations:
            new_combinations = []
            for combo in result_combinations:
                for element_combo in element_combinations:
                    new_combinations.append(combo + element_combo)
            result_combinations = new_combinations

        result_strings = [''.join(combo) for combo in result_combinations]

        if len(result_strings) > max_results:
            self.processing_steps.append(
                f"Limiting results: {len(result_strings)} combinations found, sampling {max_results}")
            result_strings = random.sample(result_strings, max_results)
        else:
            self.processing_steps.append(f"Generated {len(result_strings)} combinations")

        return result_strings

    def generate_from_regex(self, regex_str, max_results=10):
        """Generate valid combinations from a regex string."""
        self.processing_steps = []
        self.processing_steps.append(f"Processing regex: {regex_str}")

        tokens = self.tokenize(regex_str)
        parsed = self.parse(tokens)
        combinations = self.generate_combinations(parsed, max_results)

        return combinations

    def get_processing_steps(self):
        """Return the sequence of processing steps."""
        return self.processing_steps


def main():
    generator = RegexCombinationGenerator(max_repeat=5)

    regex_examples = [
        "O(P|Q|R)^(+)2(3|4)",
        "A*B(C|D|E)F(G|H|I)^(2)",
        "J^(+)K(L|M|N)*O?(P|Q)^(3)"
    ]

    for i, regex in enumerate(regex_examples, 1):
        print(f"\nExample {i}: {regex}")

        combinations = generator.generate_from_regex(regex, max_results=10)
        print("Generated combinations:")
        print("{" + ", ".join(combinations) + ", ...}")

        print("\nProcessing steps:")
        for step in generator.get_processing_steps():
            print(f"- {step}")


if __name__ == "__main__":
    main()