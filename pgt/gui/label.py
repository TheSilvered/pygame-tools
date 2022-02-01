#!/usr/bin/env python3

from typing import Union, Optional

import pygame

from .font import Font
from .gui_element import GUIElement
from pgt.constants import LEFT, RIGHT, CENTER, NO_AA, BOLD, ITALIC, UNDERLINE
from pgt.element import AniElement
from pgt.mathf import Pos
from pgt.type_hints import _col_type


class Label(GUIElement):
    def __init__(self,
       text: str = "",
       text_size: int = 20,
       color: _col_type = None,
       bg_color: _col_type = None,
       font: Union[Font, pygame.font.Font] = None,
       style: int = 0,
       alignment: int = LEFT,
       line_height: Optional[int] = None,
       adapt_to_width: bool = False,
       exceed_size: bool = True,
       auto_size: bool = False,
       *args, **kwargs):

        super().__init__(*args, **kwargs)

        self._aa = not (style & NO_AA)

        if isinstance(font, pygame.font.Font):
            self.font = font
            self.pygame_font = True
        elif isinstance(font, Font):
            self.font = font
            self.pygame_font = False
        else:
            try:
                self.font = pygame.font.Font(font, text_size)
            except FileNotFoundError:
                self.font = pygame.font.SysFont(font, text_size)
            self.pygame_font = True

        if BOLD & style and self.pygame_font:
            self.font.set_bold(True)
        if ITALIC & style and self.pygame_font:
            self.font.set_italic(True)
        if UNDERLINE & style and self.pygame_font:
            self.font.set_underline(True)

        self.__text = text
        self.adapt_width = adapt_to_width
        self.exceed_size = exceed_size
        self.alignment = alignment
        self.lines = None
        self.auto_size = auto_size

        if color is None: color = (1, 1, 1)
        self.color = color
        self.bg_color = bg_color

        if not (0 <= self.alignment <= CENTER):
            self.alignment = LEFT

        if line_height is None:
            self._line_h = self.font.get_linesize()
        else:
            self._line_h = line_height

        self.text = text

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, text):
        def check_size(this_text):
            return self.font.size(this_text)[0] > self.size.w

        self.__text = str(text)

        self.lines = self.__text.split("\n")
        if self.lines[-1] == "": del self.lines[-1]

        if self.adapt_width:
            new_lines = []
            for l in self.lines:
                words = l.split(" ")
                current_text = words[0]
                prev_text = words[0]

                while check_size(prev_text) and len(prev_text) > 1:
                    new_line = prev_text[0]
                    prev_text = prev_text[1:]
                    while prev_text and not check_size(new_line + prev_text[0]):
                        new_line += prev_text[0]
                        prev_text = prev_text[1:]
                    new_lines.append(new_line)

                for word in words[1:]:
                    current_text += " " + word
                    if check_size(current_text):
                        new_lines.append(prev_text)
                        while check_size(word) and len(word) > 1:
                            new_line = word[0]
                            word = word[1:]
                            while word and not check_size(new_line + word[0]):
                                new_line += word[0]
                                word = word[1:]
                            new_lines.append(new_line)
                        current_text = word
                        prev_text = word
                        continue

                    prev_text = current_text

                if self.font.size(current_text)[0] > self.size.w:
                    new_lines.append(prev_text)
                else:
                    new_lines.append(current_text)
            self.lines = new_lines

        if not self.lines: self.lines = [""]

        if self.exceed_size:
            width = max([self.font.size(i)[0] for i in self.lines])
            height = self._line_h * len(self.lines)
            new_image = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        else:
            new_image = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        new_image.set_colorkey((0, 0, 0))

        for l_no, i in enumerate(self.lines):
            line = self.font.render(i, self._aa, self.color, self.bg_color)

            y = self._line_h * l_no
            if self.alignment == LEFT:
                new_image.blit(line, (0, y))
            elif self.alignment == RIGHT:
                x = new_image.get_width() - self.font.size(i)[0]
                new_image.blit(line, (x, y))
            else:
                x = (new_image.get_width() - self.font.size(i)[0]) // 2
                new_image.blit(line, (x, y))

        if self.alignment == LEFT or self.auto_size:
            self.img_offset = Pos(0)
        elif self.alignment == RIGHT:
            self.img_offset = Pos(self.size.w - new_image.get_width(), 0)
        else:
            self.img_offset = Pos((self.size.w - new_image.get_width()) / 2, 0)

        self.change_image(new_image)

    def rotate(self, *args, **kwargs) -> None:
        if self.auto_size:
            super().rotate(*args, **kwargs)
        else:
            prev_size = self.size.copy()
            super().rotate(*args, **kwargs)
            self.size = prev_size


class AniLabel(Label, AniElement):
    pass
