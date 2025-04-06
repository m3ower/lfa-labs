# Laboratory Work Nr. 4: Regular Expressions

__Course: Formal Languages & Finite Automata__  

__Author: Gurev Andreea, FAF-231__

# Theory
Regular expressions (regex) are a powerful tool in formal language theory and finite automata, allowing us to define patterns within sequences of symbols. These patterns are widely used in text processing, search algorithms, lexical analysis, and even in defining the syntax of programming languages. A regular expression is essentially a **string that defines a search pattern**, often used to match, extract, or replace specific sequences within a larger text. The foundation of regular expressions is deeply connected to **finite automata**, as each regular expression can be represented by a deterministic or non-deterministic finite automaton (DFA or NFA). The fundamental components of regex include **concatenation (AB), alternation (A|B), repetition operators (*, +, ?), and grouping (parentheses)**. These constructs allow us to create expressions that can define highly specific patterns. In practical applications, regular expressions are extensively used in **compilers, search engines, data validation, and artificial intelligence models** that rely on text processing. By understanding and implementing regular expressions, we gain insight into the underlying mechanics of pattern recognition and computational linguistics.

For this lab, we focus on **generating valid sequences based on given regular expressions**. The challenge lies in correctly interpreting each regex operator and ensuring that our code adheres to the constraints provided. For example, the `*` operator means that a preceding symbol may appear **zero or more times**, while `+` ensures that it appears at least **once**. Since regex can lead to an infinite number of possible strings (especially with unbounded repetition), we impose a **limit of five repetitions** to keep output manageable. The core objective is to create an algorithm that translates a given regex into a **randomly generated valid string**, ensuring that all regex rules are followed.

# Objectives

1. Write and cover what regular expressions are, what they are used for;

2. Below you will find 3 complex regular expressions per each variant. Take a variant depending on your number in the list of students and do the following:

    a. Write a code that will generate valid combinations of symbols conform given regular expressions (examples will be shown).

    b. In case you have an example, where symbol may be written undefined number of times, take a limit of 5 times (to evade generation of extremely long combinations);

# Implementation Description
**Tokenization Implementation**
````
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
````
The tokenization method breaks down the input regex string into individual tokens that can be processed by the parser. It uses a regular expression pattern to identify common regex components like alphanumeric characters, parentheses, and operators. The implementation employs a manual parsing approach by maintaining a position counter (i) and advancing it according to the matched token length.

Special handling is provided for complex tokens like ^(+) (one or more repetitions) and ^(n) (exact repetition count) which require looking ahead in the string. For example, when encountering ^ followed by a number in parentheses, it extracts the number and creates a power token. This method effectively handles the specialized syntax used in the example patterns.

The tokenization step is crucial as it converts the raw string input into meaningful tokens that preserve the regex structure while making it easier to parse. Each step is logged for traceability.

**Parsing Implementation**
````
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
````

The parsing method converts the list of tokens into a structured representation that captures the logical structure of the regex. It builds a tree-like structure where each node represents a specific regex construct.

The implementation uses a nested helper function parse_group() to handle parenthesized groups recursively. This function processes alternation (|) by creating separate option lists for each alternative.

The main parsing loop processes tokens sequentially, building the structure according to regex rules:

• Regular characters become 'char' nodes \
• Opening parentheses trigger the parse_group() function\
• Special operators (?, *, ^(+), ^(n)) modify the preceding element by wrapping it in an appropriate node type\

The parser correctly handles operator precedence by popping the previous element and wrapping it with the operator before adding it back to the result. This creates a nested structure that accurately represents the regex semantics.

For example, when parsing A*B(C|D|E), the structure correctly captures that * applies only to A, and the group contains three alternatives.

**Combination Generation Implementation**
````
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
````

The combination generation method is the core of the implementation, responsible for producing all valid string combinations from the parsed regex structure. It uses a recursive approach with the expand_element helper function to handle each regex construct.

The expand_element function processes different node types:\
• For char nodes, it simply returns the character as a single-element list \
• For group nodes, it generates combinations for each alternative option \
• For optional nodes (?), it returns both the empty case and the case with the element \
•  For repetition nodes (star, one_or_more, power), it generates repeated combinations

The critical implementation detail for repetition is that it maintains the same alternative throughout all repetitions. For example, with (P|Q|R)^(+), it generates strings like "PP" or "QQQ" but not "PQR". This is achieved by: 
1. First generating all possible combinations for the inner element
2. For each inner combination (e.g., "P", "Q", "R"), repeating that specific combination the required number of times
3. Adding each repeated combination to the results

After generating element combinations, the function combines them to form complete strings by concatenating elements. If there are too many combinations, it randomly samples a subset to limit the output to max_results.

**Main Generation Function Implementation**

````
def generate_from_regex(self, regex_str, max_results=10):
    """Generate valid combinations from a regex string."""
    self.processing_steps = []
    self.processing_steps.append(f"Processing regex: {regex_str}")

    tokens = self.tokenize(regex_str)
    parsed = self.parse(tokens)
    combinations = self.generate_combinations(parsed, max_results)

    return combinations
````

This function serves as the main entry point for regex processing, orchestrating the entire pipeline from input string to generated combinations. It starts by resetting the processing steps log, then calls each stage in sequence:
1. Tokenize the input regex string
2. Parse the tokens into a structured representation
3. Generate combinations based on the parsed structure
4. Return the resulting combinations

This clean, sequential approach makes the code easy to follow and enables separate testing and debugging of each stage. The function accepts a max_results parameter to limit the number of combinations returned, preventing excessive output for complex patterns.

**Processing Steps Tracker Implementation**

```` 
def get_processing_steps(self):
    """Return the sequence of processing steps."""
    return self.processing_steps
````

This simple method returns the accumulated log of processing steps. Throughout the regex processing, each method appends information about what it's doing to the processing_steps list. This fulfills the bonus requirement to show the sequence of processing and provides valuable insight into how the regex is being interpreted.

The steps typically include:
1. The original regex being processed
2. The tokens extracted by the tokenizer
3. The parsed structure
4. Generation status, including the number of combinations found

This tracking is invaluable for debugging and for understanding the internal workings of the regex processor.

**Main Function Implementation**
````
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
````

The main function demonstrates the regex generator with the three example patterns provided in the requirements. For each regex pattern, it:
1. Creates a generator instance with a maximum repetition limit of 5
2. Processes the regex to generate valid combinations
3. Prints the generated combinations in a readable format
4. Shows the processing steps to provide insight into how the regex was interpreted

This function serves as both a demonstration of the generator's capabilities and a simple test to ensure it produces valid combinations for the required examples. The output format matches the expected format from the requirements, showing combinations like "OPP23" for the pattern "O(P|Q|R)^(+)2(3|4)".

The max_results parameter is set to 10 to provide a manageable number of example combinations while indicating with "..." that more combinations are possible.

# Results 
````
Example 1: O(P|Q|R)^(+)2(3|4)
Generated combinations:
{OPPP23, OQ24, OPP24, OQ23, OQQ23, OQQQ23, OQQQQ23, OQQQQ24, ORRR23, ORRRRR24, ...}

Processing steps:
- Processing regex: O(P|Q|R)^(+)2(3|4)
- Tokenizing regex: O(P|Q|R)^(+)2(3|4)
- Tokens: ['O', '(', 'P', '|', 'Q', '|', 'R', ')', '^(+)', '2', '(', '3', '|', '4', ')']
- Starting to parse tokens
- Parsed structure: [{'type': 'char', 'value': 'O'}, {'type': 'one_or_more', 'element': {'type': 'group', 'options': [['P'], ['Q'], ['R']]}}, {'type': 'char', 'value': '2'}, {'type': 'group', 'options': [['3'], ['4']]}]
- Starting to generate combinations
- Limiting results: 30 combinations found, sampling 10

Example 2: A*B(C|D|E)F(G|H|I)^(2)
Generated combinations:
{ABCFHH, AAAAABCFHH, AAAAABEFII, ABCFII, BEFHH, BCFII, AAAAABDFGG, AAAABCFII, AAAABEFGG, AAABEFII, ...}

Processing steps:
- Processing regex: A*B(C|D|E)F(G|H|I)^(2)
- Tokenizing regex: A*B(C|D|E)F(G|H|I)^(2)
- Tokens: ['A', '*', 'B', '(', 'C', '|', 'D', '|', 'E', ')', 'F', '(', 'G', '|', 'H', '|', 'I', ')', '^(2)']
- Starting to parse tokens
- Parsed structure: [{'type': 'star', 'element': {'type': 'char', 'value': 'A'}}, {'type': 'char', 'value': 'B'}, {'type': 'group', 'options': [['C'], ['D'], ['E']]}, {'type': 'char', 'value': 'F'}, {'type': 'power', 'element': {'type': 'group', 'options': [['G'], ['H'], ['I']]}, 'power': 2}]
- Starting to generate combinations
- Limiting results: 54 combinations found, sampling 10

Example 3: J^(+)K(L|M|N)*O?(P|Q)^(3)
Generated combinations:
{JJKNNNPPP, JJJJJKMMMQQQ, JJJJKLLLLLOPPP, JKOPPP, JJJJJKMMMPPP, JJJJKNNOPPP, JJJJKLLLLOPPP, JJJJKMMMOQQQ, JKLLLLLPPP, JKMOQQQ, ...}

Processing steps:
- Processing regex: J^(+)K(L|M|N)*O?(P|Q)^(3)
- Tokenizing regex: J^(+)K(L|M|N)*O?(P|Q)^(3)
- Tokens: ['J', '^(+)', 'K', '(', 'L', '|', 'M', '|', 'N', ')', '*', 'O', '?', '(', 'P', '|', 'Q', ')', '^(3)']
- Starting to parse tokens
- Parsed structure: [{'type': 'one_or_more', 'element': {'type': 'char', 'value': 'J'}}, {'type': 'char', 'value': 'K'}, {'type': 'star', 'element': {'type': 'group', 'options': [['L'], ['M'], ['N']]}}, {'type': 'optional', 'element': {'type': 'char', 'value': 'O'}}, {'type': 'power', 'element': {'type': 'group', 'options': [['P'], ['Q']]}, 'power': 3}]
- Starting to generate combinations
- Limiting results: 320 combinations found, sampling 10
````
# Conclusion
In conclusion, regular expressions are a powerful and essential tool for defining and recognizing patterns in text, widely used in programming, data validation, and search operations. Through this lab, we explored how different regex operators like `*`, `+`, `?`, `|`, and `^` work to generate structured sequences, ensuring that our code correctly interprets and applies these rules. By implementing a function that generates valid strings based on a given regex, we gained practical experience in handling **pattern matching and sequence generation**. Additionally, setting a limit on repeated characters helped us avoid infinite loops and overly long outputs. The process of breaking down the regex into steps and tracking the execution sequence allowed us to better understand how expressions are processed internally. While some challenges arose, such as handling groups of characters and ensuring correct precedence of operations, the structured approach helped us overcome these difficulties. Overall, this lab reinforced key concepts of **formal languages and finite automata**, giving us deeper insight into how regex engines work and how they can be applied in real-world scenarios.