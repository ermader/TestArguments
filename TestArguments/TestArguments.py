"""\
Command line argument processor for glyph tests.

Created on October 26, 2020

@author Eric Mader
"""

from .GlyphSpec import GlyphSpec
from .CommandLineArguments import CommandLineOption, CommandLineArgs

class TestArgs(CommandLineArgs):
    """\
    A spec object for a basic font test command line
    """
    options = [
        CommandLineOption("font", None, lambda a: a.nextExtraAsFont("font"), ("fontFile", "fontName"), (None, None)),
        CommandLineOption("glyph", lambda s, a: GlyphSpec(a), lambda a: a.nextExtra("glyph specification"), "glyphSpec", None),
        CommandLineOption("debug", None, True, "debug", False, required=False),
    ]

    def __init__(self):
        self.fontNumber = None
        CommandLineArgs.__init__(self)
        #add in our CommandLineOptions
        self._options.extend(TestArgs.options)

    def getGlyph(self, font):
        return font.glyphForName(self.glyphSpec.nameForFont(font))
