# Based on this gist: https://gist.github.com/Anomareh/6288037

import re

from markdown.extensions import Extension
from markdown.extensions.attr_list import AttrListTreeprocessor as _AttrListTreeprocessor, isheader
from markdown.util import isBlockLevel


class AttrListExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.add('attr_list', AttrListTreeprocessor(md), '>prettify')


class AttrListTreeprocessor(_AttrListTreeprocessor):
    BASE_RE = r'\{\:([^\}]*)\}'
    PARENT_RE = r'\{\^([^\}]*)\}'
    HEADER_RE = re.compile(r'[ ]+%s[ ]*$' % BASE_RE)
    BLOCK_RE = re.compile(r'\n[ ]*%s[ ]*$' % BASE_RE)
    LIST_RE = re.compile(r'\n[ ]*%s[ ]*$' % PARENT_RE)
    INLINE_RE = re.compile(r'^%s' % BASE_RE)

    def _get_last_child(self, elem):
        if len(elem):
            return self._get_last_child(elem[-1])

        return elem

    def _is_list(self, elem):
        return elem.tag in ['dl', 'ol', 'ul']

    def run(self, doc):
        for elem in doc.getiterator():
            if isBlockLevel(elem.tag):
                if self._is_list(elem):
                    lc = self._get_last_child(elem)
                    attr = None

                    if lc.tail.strip():
                        attr = 'tail'
                    elif lc.text.strip():
                        attr = 'text'

                    if attr:
                        text = getattr(lc, attr)

                        m = self.LIST_RE.search(text)

                        if m:
                            self.assign_attrs(elem, m.group(1))
                            setattr(lc, attr, text[:m.start()])

                    continue

                # Block level: check for attrs on last line of text
                RE = self.BLOCK_RE

                if isheader(elem) or elem.tag == 'dt':
                    # header or def-term: check for attrs at end of line
                    RE = self.HEADER_RE

                if len(elem) and elem.tag == 'li':
                    # special case list items. children may include a ul or ol.
                    pos = None
                    # find the ul or ol position
                    for i, child in enumerate(elem):
                        if child.tag in ['ul', 'ol']:
                            pos = i

                            break

                    if pos is None and elem[-1].tail:
                        # use tail of last child. no ul or ol.
                        m = RE.search(elem[-1].tail)

                        if m:
                            self.assign_attrs(elem, m.group(1))
                            elem[-1].tail = elem[-1].tail[:m.start()]
                    elif pos is not None and pos > 0 and elem[pos - 1].tail:
                        # use tail of last child before ul or ol
                        m = RE.search(elem[pos - 1].tail)

                        if m:
                            self.assign_attrs(elem, m.group(1))
                            elem[pos - 1].tail = elem[pos - 1].tail[:m.start()]
                    elif elem.text:
                        # use text. ul is first child.
                        m = RE.search(elem.text)

                        if m:
                            self.assign_attrs(elem, m.group(1))
                            elem.text = elem.text[:m.start()]
                elif len(elem) and elem[-1].tail:
                    # has children. Get from tail of last child
                    m = RE.search(elem[-1].tail)

                    if m:
                        self.assign_attrs(elem, m.group(1))
                        elem[-1].tail = elem[-1].tail[:m.start()]

                        if isheader(elem):
                            # clean up trailing #s
                            elem[-1].tail = elem[-1].tail.rstrip('#').rstrip()
                elif elem.text:
                    # no children. Get from text.
                    m = RE.search(elem.text)

                    if m:
                        self.assign_attrs(elem, m.group(1))
                        elem.text = elem.text[:m.start()]

                        if isheader(elem):
                            # clean up trailing #s
                            elem.text = elem.text.rstrip('#').rstrip()
            else:
                # inline: check for attrs at start of tail
                if elem.tail:
                    m = self.INLINE_RE.match(elem.tail)

                    if m:
                        self.assign_attrs(elem, m.group(1))
                        elem.tail = elem.tail[m.end():]


def makeExtension(configs=None):
    if configs is None:
        configs = {}

    return AttrListExtension(**configs)
