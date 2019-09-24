import sys

from markdown import markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.postprocessors import Postprocessor

from attr_list_parent import AttrListExtension


front_matter = """
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

        <title>DjangoCon 2019</title>

        <link rel="stylesheet" href="css/reset.css">
        <link rel="stylesheet" href="css/reveal.css">
        <link rel="stylesheet" href="css/theme/silver.css">

        <!-- Theme used for syntax highlighting of code -->
        <link rel="stylesheet" href="lib/css/monokai.css">

        <!-- Printing and PDF exports -->
        <script>
            var link = document.createElement( 'link' );
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
            document.getElementsByTagName( 'head' )[0].appendChild( link );
        </script>
    </head>
    <body>
        <div class="reveal">
            <div class="slides">
"""

end_matter = """
            </div>
        </div>

        <script src="js/reveal.js"></script>

        <script>
            // More info about config & dependencies:
            // - https://github.com/hakimel/reveal.js#configuration
            // - https://github.com/hakimel/reveal.js#dependencies
            Reveal.initialize({
                progress: true,
                center: false,
                controls: true,
                hash: true,
                dependencies: [
                    { src: 'plugin/markdown/marked.js' },
                    { src: 'plugin/markdown/markdown.js' },
                    { src: 'plugin/notes/notes.js', async: true },
                    { src: 'plugin/highlight/highlight.js', async: true }
                ]
            });
        </script>
    </body>
</html>

"""


class SectionPostProcessor(Postprocessor):
    def run(self, text):
        text = text.replace('<hr />', '</section><section>')
        return f'<section>\n{text}\n</section>'


class SectionExtension(Extension):
    def extendMarkdown(self, md):
        md.postprocessors.register(SectionPostProcessor(md), 'section_post_processor', 175)


def main():
    with open(sys.argv[1]) as f:
        text = f.read()

    html = markdown(text, extensions=[
        'markdown.extensions.extra',
        AttrListExtension(),
        SectionExtension(),
        CodeHiliteExtension(noclasses=True, pygments_style='monokai'),
        'markdown.extensions.smarty'
    ])

    print(front_matter)
    print(html)
    print(end_matter)


if __name__ == '__main__':
    main()
