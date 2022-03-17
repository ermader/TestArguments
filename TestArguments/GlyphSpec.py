"""\
Process glyph specs like "/name", "uni04C0", "l" and "gid400"

Created on July 5, 2021

@author Eric Mader
"""

from __future__ import annotations

import typing

import re

from .Font import Font

nameRE = re.compile(r"/(.+)")
uniRE = re.compile(r"uni([0-9a-fA-F]{4,6})")
gidRE = re.compile(r"gid([0-9]{1,5})")


class GlyphSpec(object):
    name = 0
    charCode = 1
    glyphID = 2
    unknown = 3

    __slots__ = "_spec", "_type"

    @classmethod
    def specFromName(cls, name: str):
        return f"/{name}" if name else None

    @classmethod
    def specFromCharCode(cls, charCode: int):
        return f"uni{charCode:04X}" if charCode else None

    @classmethod
    def specFromGlyphID(cls, gid: int):
        return f"gid{gid}" if gid else None

    def __init__(self, glyphSpec: str):
        if len(glyphSpec) == 1:
            self._spec = ord(glyphSpec)
            self._type = GlyphSpec.charCode
            return

        m = nameRE.fullmatch(glyphSpec)
        if m:
            self._spec = m.group(1)
            self._type = GlyphSpec.name
            return

        m = uniRE.fullmatch(glyphSpec)
        if m:
            self._spec = int(m.group(1), base=16)
            self._type = GlyphSpec.charCode
            return

        m = gidRE.fullmatch(glyphSpec)
        if m:
            self._spec = int(m.group(1))
            self._type = GlyphSpec.glyphID
            return

        self._spec = ""
        self._type = GlyphSpec.unknown

    def __eq__(self, other: object):
        otherSpec = typing.cast(GlyphSpec, other)
        return self._spec == otherSpec._spec and self._type == otherSpec._type

    def __ne__(self, other: object):
        otherSpec = typing.cast(GlyphSpec, other)
        return self._type != otherSpec._type or self._spec != otherSpec._spec

    @property
    def spec(self):
        return self._spec

    @property
    def type(self):
        return self._type

    def nameForFont(self, font: Font):
        if self._type == GlyphSpec.charCode:
            return font.glyphNameForCharacterCode(typing.cast(int, self._spec))

        if self._type == GlyphSpec.glyphID:
            spec = typing.cast(int, self._spec)
            names = font.glyphNames()
            return names[spec] if spec < len(names) else ""

        if self._type == GlyphSpec.name:
            names = font.glyphNames()
            spec = typing.cast(str, self._spec)
            return spec if spec in names else ""

        return ""  # None

    def glyphIDForFont(self, font: Font):
        name = self.nameForFont(font)
        names = font.glyphNames()

        try:
            return names.index(name)
        except ValueError:
            return None

    def charCodeForFont(self, font: Font):
        charName = self.nameForFont(font)
        cmap = font._ttFont.getBestCmap()

        for code, name in cmap.items():
            if name == charName:
                return code

        return None

    def nameSpecForFont(self, font: Font):
        return self.specFromName(self.nameForFont(font))

    def glyphIDSpecForFont(self, font: Font):
        glyphID = typing.cast(int, self.glyphIDForFont(font))
        return self.specFromGlyphID(glyphID)

    def charCodeSpecForFont(self, font: Font):
        charCode = typing.cast(int, self.charCodeForFont(font))
        return self.specFromCharCode(charCode)
