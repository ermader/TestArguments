"""\
Font.py

Created on July 30, 2021
Based on GTFont from GlyphTest.py

@author Eric Mader
"""

from fontTools.ttLib import ttFont, TTLibError
from FontDocTools.Font import Font as FDTFont, Glyph as FDTGlyph

class Font(FDTFont):
    def __init__(self, fontFile, fontName=None, fontNumber=None):
        FDTFont.__init__(self, fontFile, fontName, fontNumber)

    def __contains__(self, item):
        return item in self._ttFont

    def __getitem__(self, item):
        return self._ttFont[item]

    @property
    def postscriptName(self):
        # return self.fontNameEntry(6, None)  # postscript name is the same in any language
        return self._getPostScriptName(self._ttFont)  # use this until language == None bug fixed in fontNameEntry.

    @property
    def fullName(self):
        return self.fontNameEntry(4, "en")

    @property
    def familyName(self):
        return self.fontNameEntry(1, "en")

    def glyphNameForCharacterCode(self, charCode):
        return self._ttFont.getBestCmap().get(charCode, "")

    @property
    def glyphSet(self):
        return self._ttFont.getGlyphSet()

    @property
    def hmtxMetrics(self):
        if not self._hMetrics:
            self._hMetrics = self["hmtx"].metrics
        return self._hMetrics

    @property
    def vmtxMetrics(self):
        if not self._vMetrics and "vmtx" in self:
            self._vMetrics = self["vmtx"].metrics
        return self._vMetrics

    @property
    def typographicAscender(self):
        return self.fontMetric("OS/2", "sTypoAscender")

    @property
    def typographicDescender(self):
        return self.fontMetric("OS/2", "sTypoDescender")

    def __str__(self):
        return self.postscriptName

    def glyphForName(self, glyphName):
        """\
        Returns the glyph with the given name.
        """
        glyphs = self._glyphs
        if glyphName in glyphs:
            return glyphs[glyphName]
        if glyphName not in self._ttGlyphSet:
            raise ValueError(f"Unknown glyph name: “{glyphName}”.")
        # glyph = GTGlyph(self, glyphName)
        glyph = FDTGlyph(glyphName, self._ttGlyphName(glyphName), self)
        glyphs[glyphName] = glyph
        return glyph


    def glyphForIndex(self, index):
        """\
        Returns the glyph with the given glyph index.
        """
        return self.glyphForName(self.glyphName(index))


    def glyphForCharacter(self, char):
        """\
        Returns the nominal glyph for the given Unicode character.
        """

        charCode = ord(char) if type(char) == type("") else char
        return self.glyphForName(self.glyphNameForCharacterCode(charCode))

    def unicodeForName(self, charName):
        for code, name in self._ttFont.getBestCmap().items():
            if name == charName:
                return code

        return None

    def hasCharacterCode(self, char):
        charCode = ord(char) if type(char) == type("") else char
        cmap = self._ttFont.getBestCmap()
        return char in cmap.keys()

    def hasGlyphName(self, glyphName):
        names = self.glyphNames()
        return glyphName in names

    def hasGlyphIndex(self, glyphIndex):
        names = self.glyphNames()
        return glyphIndex < len(names)
