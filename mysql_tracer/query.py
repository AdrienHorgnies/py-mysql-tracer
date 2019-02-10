import re


class Query:

    def __init__(self, source):
        self.source = source
        self.__query_str = None

    @property
    def query_str(self):
        if self.__query_str is not None:
            return self.__query_str
        else:
            self.__query_str = ' '.join([
                normalize_space(strip_inline_comment(line).strip())
                for line in open(self.source)
                if not is_comment(line) and not is_blank(line)
            ])
            return self.__query_str


def normalize_space(line):
    return re.sub(' +', ' ', line)


def strip_inline_comment(line):
    return re.sub('--.*', '',
                  re.sub('#.*', '', line))


def is_blank(line):
    return not line.strip()


def is_comment(line):
    return line.strip().startswith('--') or line.strip().startswith('#')
