import re

from blib.citekey import article_citekey, misc_citekey
from blib.utils import normalise_unicode_to_ascii


class BibDeskFormatError(ValueError):
    pass


class BibDeskAutogenerationFormatter:
    def __init__(self, format_string, encoder, citekey_mode=False):
        self._format_string = format_string
        self._encoder = encoder
        self._citekey_mode = citekey_mode

    def format(self, data):
        result = []
        i = 0
        while i < len(self._format_string):
            char = self._format_string[i]
            if char != '%':
                result.append(self._encode_literal(char))
                i += 1
                continue

            if i + 1 >= len(self._format_string):
                raise BibDeskFormatError("dangling '%' in format string")

            specifier = self._format_string[i + 1]
            text, i = self._expand_specifier(specifier, i + 2, data)
            result.append(text)

        return ''.join(result)

    def _expand_specifier(self, specifier, index, data):
        if specifier in '%[]-0123456789':
            return self._encode_literal(specifier), index

        if specifier in 'uUn':
            raise BibDeskFormatError(f"specifier %{specifier} is not supported for blib output formatting")

        if specifier in 'aApP':
            options, index = self._parse_square_brackets(index)
            index = self._consume_parameter_spacing(index)
            number_text, index = self._parse_author_numbers(index, specifier)
            return self._format_people(specifier, options, number_text, data), index

        if specifier in 'tTk':
            options, index = self._parse_square_brackets(index)
            index = self._consume_parameter_spacing(index)
            number_text, index = self._parse_number(index)
            return self._format_simple_specifier(specifier, options, number_text, data), index

        if specifier in 'lLeb':
            return self._format_file_specifier(specifier, [], data), index

        if specifier == 'E':
            options, index = self._parse_square_brackets(index)
            return self._format_file_specifier(specifier, options, data), index

        if specifier in 'fwcsi':
            field_name, index = self._parse_field_name(index)
            options, index = self._parse_square_brackets(index)
            index = self._consume_parameter_spacing(index)
            number_text, index = self._parse_number(index)
            return self._format_field_specifier(specifier, field_name, options, number_text, data), index

        if specifier in 'yYm':
            return self._format_date_specifier(specifier, data), index

        raise BibDeskFormatError(f"unknown format specifier %{specifier}")

    def _format_people(self, specifier, options, number_text, data):
        prefer_editor = specifier in 'pP'
        people = self._people(data, prefer_editor=prefer_editor)
        if not people:
            return ''

        name_separator = options[0] if len(options) >= 1 else ''
        max_names = 0
        max_name_length = 0

        if specifier in 'aApP':
            max_names = number_text[0] if len(number_text) >= 1 else 0
        if specifier in 'ap':
            max_name_length = number_text[1] if len(number_text) >= 2 else 0

        etal_text = ''
        if specifier in 'aApP':
            if specifier in 'AP':
                initial_separator = options[1] if len(options) >= 2 else ''
                etal_text = options[2] if len(options) >= 3 else ''
            else:
                initial_separator = ''
                etal_text = options[1] if len(options) >= 2 else ''
        else:
            initial_separator = ''

        selected_people, truncated = self._selected_people(people, max_names)
        etal_count = None
        if etal_text and etal_text[-1].isdigit():
            etal_count = int(etal_text[-1])
            etal_text = etal_text[:-1]

        if truncated and etal_count is not None:
            if max_names < 0:
                selected_people = selected_people[-etal_count:]
            else:
                selected_people = selected_people[:etal_count]

        if specifier in 'ap':
            rendered_people = [
                self._encode_generated(self._prepare_generated_text(self._truncate(name['family'], max_name_length)))
                for name in selected_people
            ]
        else:
            rendered_people = [
                self._encode_generated(self._name_with_initials(name, initial_separator))
                for name in selected_people
            ]

        rendered = name_separator.join(rendered_people)
        if truncated and etal_text:
            rendered += self._encode_generated(etal_text)

        return rendered

    def _format_simple_specifier(self, specifier, options, number_text, data):
        if specifier == 't':
            value = self._prepare_generated_text(self._field_text(data, 'title'))
            max_length = int(number_text) if number_text else 0
            return self._encode_generated(self._truncate(value, max_length))

        if specifier == 'T':
            ignore_length = int(options[0]) if options and options[0] else 3
            max_words = int(number_text) if number_text else 0
            value = self._words_from_text(self._field_text(data, 'title'), ignore_length, max_words)
            value = self._prepare_generated_text(value)
            return self._encode_generated(value)

        if specifier == 'k':
            slash_replacement = options[0] if len(options) >= 1 and options[0] else '/'
            separator = options[1] if len(options) >= 2 else ''
            max_keywords = int(number_text) if number_text else 0
            keywords = self._keywords(data)
            if max_keywords > 0:
                keywords = keywords[:max_keywords]
            keywords = [self._replace_slashes(keyword, slash_replacement) for keyword in keywords]
            value = self._prepare_generated_text(separator.join(keywords))
            return self._encode_generated(value)

        raise BibDeskFormatError(f"unsupported simple specifier %{specifier}")

    def _format_file_specifier(self, specifier, options, data):
        if specifier == 'b':
            bibliography = data.get('bibliography-file')
            if not bibliography:
                raise BibDeskFormatError("specifier %b requires bibliography-file metadata which is not available")
            return self._encode_generated(re.sub(r'\.[^.]*$', '', bibliography))

        linked_file = data.get('linked-file')
        if not linked_file:
            raise BibDeskFormatError(f"specifier %{specifier} requires linked-file metadata which is not available")

        base_name, extension = re.match(r'^(.*?)(\.[^.]*)?$', linked_file).groups()

        if specifier == 'l':
            return self._encode_generated(base_name)
        if specifier == 'L':
            return self._encode_generated(linked_file)
        if specifier == 'e':
            return self._encode_generated(extension or '')
        if specifier == 'E':
            default_extension = options[0] if options else ''
            if extension:
                return self._encode_generated(extension.removeprefix('.'))
            return self._encode_generated(default_extension)

        raise BibDeskFormatError(f"unsupported file specifier %{specifier}")

    def _format_field_specifier(self, specifier, field_name, options, number_text, data):
        if specifier == 'f':
            value = self._field_text(data, field_name)
            slash_replacement = options[0] if len(options) >= 1 and options[0] else '/'
            max_length = int(number_text) if number_text else 0
            value = self._replace_slashes(value, slash_replacement)
            value = self._prepare_generated_text(value)
            return self._encode_generated(self._truncate(value, max_length))

        if specifier == 'w':
            value = self._field_text(data, field_name)
            separator_characters = options[0] if len(options) >= 1 else ''
            slash_replacement = options[1] if len(options) >= 2 and options[1] else '/'
            separator = options[2] if len(options) >= 3 else ''
            max_words = int(number_text) if number_text else 0
            value = self._words_from_field(value, separator_characters, slash_replacement, separator, max_words)
            value = self._prepare_generated_text(value)
            return self._encode_generated(value)

        if specifier == 'c':
            value = self._field_text(data, field_name)
            ignore_length = int(number_text) if number_text else 3
            value = self._prepare_generated_text(self._initials_from_field(value, ignore_length))
            return self._encode_generated(value)

        if specifier == 's':
            value = self._field_value(data, field_name)
            yes_value = options[0] if len(options) >= 1 else ''
            no_value = options[1] if len(options) >= 2 else ''
            mixed_value = options[2] if len(options) >= 3 else yes_value
            max_length = int(number_text) if number_text else 0
            if isinstance(value, list):
                if len(value) > 1:
                    return self._encode_generated(self._truncate(self._prepare_generated_text(mixed_value), max_length))
                if len(value) == 1:
                    return self._encode_generated(self._truncate(self._prepare_generated_text(yes_value), max_length))
                return self._encode_generated(self._truncate(self._prepare_generated_text(no_value), max_length))
            if value:
                return self._encode_generated(self._truncate(self._prepare_generated_text(yes_value), max_length))
            return self._encode_generated(self._truncate(self._prepare_generated_text(no_value), max_length))

        if specifier == 'i':
            document_info = data.get('document-info', {})
            value = document_info.get(field_name, '')
            max_length = int(number_text) if number_text else 0
            value = self._prepare_generated_text(str(value))
            return self._encode_generated(self._truncate(value, max_length))

        raise BibDeskFormatError(f"unsupported field specifier %{specifier}")

    def _format_date_specifier(self, specifier, data):
        year = str(data.get('year', '') or '')
        month = str(data.get('month', '') or '')
        if specifier == 'y':
            return self._encode_generated(year[-2:] if year else '')
        if specifier == 'Y':
            return self._encode_generated(year)
        if specifier == 'm':
            return self._encode_generated(month)
        raise BibDeskFormatError(f"unsupported date specifier %{specifier}")

    def _consume_parameter_spacing(self, index):
        while index < len(self._format_string) and self._format_string[index].isspace():
            next_index = index + 1
            if next_index < len(self._format_string) and (
                self._format_string[next_index].isdigit()
                or (
                    self._format_string[next_index] == '-'
                    and next_index + 1 < len(self._format_string)
                    and self._format_string[next_index + 1].isdigit()
                )
            ):
                index += 1
                continue
            break
        return index

    def _parse_square_brackets(self, index):
        options = []
        while index < len(self._format_string) and self._format_string[index] == '[':
            index += 1
            option = []
            while index < len(self._format_string):
                char = self._format_string[index]
                if char == ']':
                    index += 1
                    break
                if char == '%':
                    if index + 1 >= len(self._format_string):
                        raise BibDeskFormatError("dangling '%' inside [] in format string")
                    escaped = self._format_string[index + 1]
                    if escaped not in '%[]-0123456789':
                        raise BibDeskFormatError("only escaped characters are allowed inside []")
                    option.append(escaped)
                    index += 2
                    continue
                option.append(char)
                index += 1
            else:
                raise BibDeskFormatError("unterminated [] in format string")
            options.append(''.join(option))
        return options, index

    def _parse_field_name(self, index):
        if index >= len(self._format_string) or self._format_string[index] != '{':
            raise BibDeskFormatError("field-based specifiers require a {Field} parameter")

        index += 1
        field_name = []
        while index < len(self._format_string) and self._format_string[index] != '}':
            field_name.append(self._format_string[index])
            index += 1

        if index >= len(self._format_string):
            raise BibDeskFormatError("unterminated {Field} in format string")

        return ''.join(field_name), index + 1

    def _parse_author_numbers(self, index, specifier):
        if index >= len(self._format_string):
            return (), index

        max_names = None
        max_name_length = None

        if self._format_string[index] == '-' and index + 1 < len(self._format_string) and self._format_string[index + 1].isdigit():
            max_names = -int(self._format_string[index + 1])
            index += 2
        elif self._format_string[index].isdigit():
            max_names = int(self._format_string[index])
            index += 1

        if specifier in 'ap' and index < len(self._format_string) and self._format_string[index].isdigit():
            max_name_length = int(self._format_string[index])
            index += 1

        values = []
        if max_names is not None:
            values.append(max_names)
        if max_name_length is not None:
            values.append(max_name_length)
        return tuple(values), index

    def _parse_number(self, index):
        if index >= len(self._format_string):
            return '', index

        start = index
        if self._format_string[index] == '-':
            index += 1
        while index < len(self._format_string) and self._format_string[index].isdigit():
            index += 1
        if index == start or (index == start + 1 and self._format_string[start] == '-'):
            return '', start
        return self._format_string[start:index], index

    def _people(self, data, prefer_editor=False):
        if prefer_editor and data.get('editor'):
            return data['editor']
        return data.get('author', [])

    def _selected_people(self, people, max_names):
        if max_names == 0 or abs(max_names) >= len(people):
            return list(people), False
        if max_names < 0:
            return list(people[max_names:]), True
        return list(people[:max_names]), True

    def _name_with_initials(self, person, initial_separator):
        initials = []
        given_name = person.get('given', '')
        if isinstance(given_name, list):
            given_name = ' '.join(given_name)
        for name in str(given_name).split():
            if not name:
                continue
            initials.append(name[:-1] if name.endswith('.') else name[0])
        if initials:
            return f'{person["family"]}{initial_separator}{".".join(initials)}.'
        return person['family']

    def _truncate(self, text, max_length):
        if max_length <= 0:
            return text
        return text[:max_length]

    def _replace_slashes(self, text, replacement):
        if replacement == '/':
            return text
        return text.replace('/', replacement)

    def _field_value(self, data, field_name):
        normalized = self._normalize_field_name(field_name)
        if normalized == 'citekey':
            if data.get('bibtex_type') == 'article':
                return article_citekey(data)
            return misc_citekey(data)
        if normalized == 'pages':
            return self._pages_text(data)

        for key, value in data.items():
            if self._normalize_field_name(key) == normalized:
                return value

        return ''

    def _field_text(self, data, field_name):
        value = self._field_value(data, field_name)
        if value is None:
            return ''
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                names = []
                for person in value:
                    given = person.get('given', '')
                    if isinstance(given, list):
                        given = ' '.join(given)
                    parts = [str(given).strip(), person.get('family', '').strip()]
                    names.append(' '.join(part for part in parts if part))
                return ', '.join(names)
            return ', '.join(str(item) for item in value)
        return str(value)

    def _pages_text(self, data):
        pages = data.get('pages')
        if pages is None:
            return ''
        if isinstance(pages, list):
            if len(pages) == 1:
                return str(pages[0])
            return '--'.join(str(page) for page in pages)
        return str(pages)

    def _keywords(self, data):
        keywords = data.get('keywords', [])
        if isinstance(keywords, str):
            return [keyword.strip() for keyword in re.split(r'[;:,]', keywords) if keyword.strip()]
        return [str(keyword) for keyword in keywords]

    def _words_from_text(self, text, ignore_length, max_words):
        if max_words <= 0:
            return text

        words = text.split()
        counted_words = 0
        result = []
        for word in words:
            result.append(word)
            plain_word = re.sub(r'^[^\w]+|[^\w]+$', '', word, flags=re.UNICODE)
            if len(plain_word) > ignore_length:
                counted_words += 1
                if counted_words >= max_words:
                    break

        return ' '.join(result)

    def _words_from_field(self, text, separator_characters, slash_replacement, separator, max_words):
        replaced_text = self._replace_slashes(text, slash_replacement)
        if separator_characters:
            parts = [part for part in re.split(f'[{re.escape(separator_characters)}]+', replaced_text) if part]
        else:
            parts = re.findall(r'[\w]+', replaced_text, flags=re.UNICODE)

        if max_words > 0:
            parts = parts[:max_words]

        return separator.join(parts)

    def _initials_from_field(self, text, ignore_length):
        parts = re.findall(r'[\w]+', text, flags=re.UNICODE)
        initials = [part[0] for part in parts if len(part) > ignore_length]
        return ''.join(initials)

    def _normalize_field_name(self, field_name):
        return re.sub(r'[^a-z0-9]+', '', field_name.lower())

    def _prepare_generated_text(self, text):
        if not self._citekey_mode:
            return text

        normalized = normalise_unicode_to_ascii(text)
        normalized = re.sub(r'\s+', '-', normalized)
        normalized = re.sub(r'[^A-Za-z0-9:;./-]+', '', normalized)
        normalized = re.sub(r'-{2,}', '-', normalized)
        return normalized

    def _encode_generated(self, text):
        return self._encode_text(text)

    def _encode_literal(self, text):
        return self._encode_text(text, fallback_to_raw=True)

    def _encode_text(self, text, fallback_to_raw=False):
        try:
            return self._encoder.encode(text)
        except RuntimeError:
            if fallback_to_raw:
                return text
            raise
