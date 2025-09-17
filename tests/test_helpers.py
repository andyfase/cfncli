"""Shared test helper functions for pprint tests."""


def has_key_value_format(lines, key, indent_level, value=None):
    """Check if a key-value pair exists with proper indentation and optionally check value.

    Args:
        lines: List of output lines
        key: The key to look for
        indent_level: Expected indentation level
        value: Expected value (string) or values (list) after the key
    """
    expected_key = " " * indent_level + key + ": "

    for i, line in enumerate(lines):
        if line == expected_key:
            if value is None:
                return True

            # Handle array of values - check if all values appear in sequence after the key
            if isinstance(value, list):
                found_values = []
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    if next_line and next_line.strip():  # Skip empty lines
                        found_values.append(next_line)
                        if len(found_values) >= len(value):
                            break
                if found_values == [str(v) for v in value]:
                    return True
                # Continue to check other occurrences of the key
                continue

            # Handle single value
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                if next_line is not None and str(next_line).strip():  # Skip empty lines, handle integers
                    if str(value) == str(next_line) or str(value) in str(next_line):
                        return True
                    break  # Move to next occurrence of the key
    return False


def has_resource_format(lines, resource_name, resource_type, indent_level=2):
    """Check if a resource is formatted correctly."""
    expected_format = " " * indent_level + f"{resource_name} ({resource_type}): "
    return expected_format in lines


def has_indented_text(lines, text, indent_level):
    """Check if text appears with specific indentation."""
    expected_format = " " * indent_level + text
    return any(line.startswith(expected_format) for line in lines)
