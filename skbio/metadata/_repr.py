# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import itertools
import numbers
import textwrap

from abc import ABCMeta, abstractmethod
from skbio._base import ElasticLines


class _MetadataReprBuilder(metaclass=ABCMeta):
    """Abstract base class for building  a repr for an object containing
    metadata and/or positional metadata.

    Parameters
    ----------
    obj : Type varies depending on subclass
        Object to build repr for.
    width : int
        Maximum width of the repr.
    indent : int
        Number of spaces to use for indented lines.
    """
    def __init__(self, obj, width, indent):
        self._obj = obj
        self._width = width
        self._indent = ' ' * indent

    @abstractmethod
    def _process_header(self):
        """Used by `build` Template Method to build header for the repr"""

    @abstractmethod
    def _process_data(self):
        """Used by `build` Template Method to build data lines for the repr"""

    def build(self):
        """Template method for building the repr"""

        self._lines = ElasticLines()

        self._process_header()
        self._process_metadata()
        self._process_positional_metadata()
        self._process_features()
        self._process_stats()
        self._process_data()

        return self._lines.to_str()

    def _process_metadata(self):
        if self._obj.metadata:
            self._lines.add_line('Metadata:')
            # Python 3 doesn't allow sorting of mixed types so we can't just
            # use sorted() on the metadata keys. Sort first by type then sort
            # by value within each type.
            for key in self._sorted_keys_grouped_by_type(self._obj.metadata):
                value = self._obj.metadata[key]
                self._lines.add_lines(
                    self._format_metadata_key_value(key, value))

    def _process_features(self):
        """
        TODO:
        This can generate an enormous amount of output. Another option would be to
        output the feature 'types' and number found in this sequence rather than all the
        details.
        """
        if self._obj.features:
            self._lines.add_lines(self._format_feature_key_value('Features', 'Location/Qualifiers', 1))
            for feature in self._obj.features:
                self._lines.add_lines(self._format_feature_key_value(feature.type_, feature.location, 2))
                for key in sorted(feature.qualifiers):
                    value = feature.qualifiers[key]
                    if isinstance(value, list):
                        for v in value:
                            self._lines.add_lines(self._format_feature_key_value(key, v, 3))
                    else:
                        self._lines.add_lines(self._format_feature_key_value(key, value, 3))

    def _sorted_keys_grouped_by_type(self, dict_):
        """Group keys within a dict by their type and sort within type."""
        type_sorted = sorted(dict_, key=self._type_sort_key)
        type_and_value_sorted = []
        for _, group in itertools.groupby(type_sorted, self._type_sort_key):
            type_and_value_sorted.extend(sorted(group))
        return type_and_value_sorted

    def _type_sort_key(self, key):
        return repr(type(key))

    def _format_metadata_key_value(self, key, value):
        """Format metadata key:value, wrapping across lines if necessary."""
        key_fmt = self._format_key(key)

        supported_type = True
        if isinstance(value, str):
            # extra indent of 1 so that wrapped text lines up:
            #
            #     'foo': 'abc def ghi
            #             jkl mno'
            value_repr = repr(value)
            extra_indent = 1
        elif isinstance(value, bytes):
            # extra indent of 2 so that wrapped text lines up:
            #
            #     'foo': b'abc def ghi
            #              jkl mno'
            value_repr = repr(value)
            extra_indent = 2
        # handles any number, this includes bool
        elif value is None or isinstance(value, numbers.Number):
            value_repr = repr(value)
            extra_indent = 0
        else:
            supported_type = False

        if not supported_type or len(value_repr) > 140:
            value_repr = str(type(value))
            # extra indent of 1 so that wrapped text lines up past the bracket:
            #
            #     'foo': <type
            #             'dict'>
            extra_indent = 1

        return self._wrap_text_with_indent(value_repr, key_fmt, extra_indent)

    def _format_feature_key_value(self, key, value, indent=1):
        """Format feature type, location, and qualifiers, wrapping across lines if
           necessary. only expecting strings as key and value types
        """
        key_fmt = (self._indent * indent) + str(key)

        if isinstance(value, str):
            value_repr = str(value)
            extra_indent = 1
        else:
            value_repr = repr(value)
            extra_indent = 0

        if indent == 3:
            key_fmt += '='
        elif indent == 2:
            value_repr = self._indent + value_repr

        return self._wrap_text_with_indent(value_repr, key_fmt, extra_indent)

    def _process_positional_metadata(self):
        if len(self._obj.positional_metadata.columns):
            self._lines.add_line('Positional metadata:')
            for key in self._obj.positional_metadata.columns.values.tolist():
                dtype = self._obj.positional_metadata[key].dtype
                self._lines.add_lines(
                    self._format_positional_metadata_column(key, dtype))

    def _format_positional_metadata_column(self, key, dtype):
        key_fmt = self._format_key(key)
        dtype_fmt = '<dtype: %s>' % str(dtype)
        return self._wrap_text_with_indent(dtype_fmt, key_fmt, 1)

    def _format_key(self, key):
        """Format metadata key.

        Includes initial indent and trailing colon and space:

            <indent>'foo':<space>

        """
        key_fmt = self._indent + repr(key)
        supported_types = (str, bytes, numbers.Number, type(None))
        if len(key_fmt) > (self._width / 2) or not isinstance(key,
                                                              supported_types):
            key_fmt = self._indent + str(type(key))
        return '%s: ' % key_fmt

    def _wrap_text_with_indent(self, text, initial_text, extra_indent):
        """Wrap text across lines with an initial indentation.

        For example:

            'foo': 'abc def
                    ghi jkl
                    mno pqr'

        <indent>'foo':<space> is `initial_text`. `extra_indent` is 1. Wrapped
        lines are indented such that they line up with the start of the
        previous line of wrapped text.

        """
        return textwrap.wrap(
            text, width=self._width, expand_tabs=False,
            initial_indent=initial_text,
            subsequent_indent=' ' * (len(initial_text) + extra_indent))

    def _process_stats(self):
        self._lines.add_line('Stats:')
        for label, value in self._obj._repr_stats():
            self._lines.add_line('%s%s: %s' % (self._indent, label, value))
        self._lines.add_separator()
