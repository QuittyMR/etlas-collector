import re


class StringUtils(object):
    @staticmethod
    def snake_to_camel(camel_cased_string: str, is_lower: bool = False) -> str:
        word_elements = [string.capitalize() for string in camel_cased_string.split('_')]

        if is_lower:
            word_elements[0] = word_elements[0].lower()

        return ''.join(word_elements)

    @staticmethod
    def camel_to_snake(snake_cased_string: str) -> str:
        word_elements = [word.lower() for word in re.sub(r'([A-Z])', r'_\1' ,snake_cased_string).split('_')]

        if not word_elements[0]:
            word_elements = word_elements[1:]

        return '_'.join(word_elements)
