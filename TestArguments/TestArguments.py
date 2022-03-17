"""\
Command line argument processor for glyph tests.

Created on October 26, 2020

@author Eric Mader
"""

import typing

from .GlyphSpec import GlyphSpec
from .CommandLineArguments import CommandLineOption, CommandLineArgs
from .Font import Font


class TestArgs(CommandLineArgs):
    """\
    A spec object for a basic font test command line
    """

    options = [
        CommandLineOption(
            "font",
            None,
            lambda a: a.nextExtraAsFont("font"),
            ("fontFile", "fontName"),
            (None, None),
        ),
        CommandLineOption(
            "glyph",
            lambda s, a: GlyphSpec(a),
            lambda a: a.nextExtra("glyph specification"),
            "glyphSpec",
            None,
        ),
        CommandLineOption("debug", None, True, "debug", False, required=False),
    ]

    def __init__(self):
        self.fontFile: str = ""
        self.fontName: typing.Optional[str] = None
        self.fontNumber: typing.Optional[int] = None
        self.debug: bool = False
        CommandLineArgs.__init__(self)
        # add in our CommandLineOptions
        self._options.extend(TestArgs.options)
        self.glyphSpec = GlyphSpec(
            "gid0"
        )  # this is only here to keep type checking happy... could use GlyphSpec | None, but then have to check for None below...

    def getGlyph(self, font: Font):
        return font.glyphForName(self.glyphSpec.nameForFont(font))
