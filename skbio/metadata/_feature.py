from skbio._base import SkbioObject
from skbio.util._decorator import experimental
from skbio._base import ElasticLines
import textwrap



class Feature(SkbioObject):
    """
    Stores genbank sequence feature records
    """

    @experimental(as_of="0.4.2")
    def __init__(self, type, location, qualifiers = None):
        self.type_ = type

        # original location string is kept as well as parsed into
        # attributes describing location
        self.location = location
        self.rc_ = False
        self.left_partial_ = False
        self.right_partial_ = False
        self.begin = 0
        self.end = 0
        self.qualifiers = qualifiers

    @experimental(as_of="0.4.2")
    def __str__(self):
        # TODO: string output for debugging/stdout display
        key_field = 10
        value_field = 60
        spaces = ' ' * key_field
        type_format = ''.join(['{:',str(key_field),'s}{:',str(value_field),'}'])
        fq0 = lambda k,v: spaces + k + '=' + v
        fq1 = lambda k,v: type_format.format(k,v)
        lines = ElasticLines()
        lines.add_line(fq1(self.type_, self.location))
        for key in sorted(self.qualifiers):
            value = self.qualifiers[key]
            if isinstance(value, list):
                for v in value:
                    lines.add_line(fq0(key, v))
            else:
                lines.add_line(fq0(key, value))
        return lines.to_str()


    @experimental(as_of="0.4.2")
    def __repr__(self):
        # TODO: string output that meet genbank file specification
        pass


    def _wrap_text_with_indent(self, text, initial_text, extra_indent):
        """Wrap text across lines with an initial indentation.

        For example:

            'foo': 'abc def
                    ghi jkl
                    mno pqr'

        <indent>'foo':<space> is `initial_text`. `extra_indent` is 1. Wrapped
        lines are indented such that they line up with the start of the
        previous line of wrapped text.

        TODO: taken from metadata/_repr.py.

        """
        return textwrap.wrap(
            text, width=self._width, expand_tabs=False,
            initial_indent=initial_text,
            subsequent_indent=' ' * (len(initial_text) + extra_indent))


