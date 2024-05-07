import time


class LCD:
    def __init__(self, i2c, address=0x27, backlight_enabled=True, display_width=16):
        self.i2c = i2c
        self.addr = address
        self.backlight_val = 0x08 if backlight_enabled else 0x00
        self.display_width = display_width
        self.init_lcd()

    def init_lcd(self):
        """ Initializing the display and backlight """
        commands = [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]
        for cmd in commands:
            self.send_cmd(cmd)
        self.toggle_backlight(True)
        time.sleep_ms(50)

    def toggle_backlight(self, state):
        """ Backlight control """
        self.backlight_val = 0x08 if state else 0x00
        self.send_cmd(0x00)  # Update if 0x00 doesn't control backlight

    def send_cmd(self, cmd):
        """ Sending a command to display """
        high_nibble = cmd & 0xF0
        low_nibble = (cmd << 4) & 0xF0
        self.i2c.writeto(self.addr, bytearray([high_nibble | self.backlight_val | 0x04, high_nibble | self.backlight_val,
                                               low_nibble | self.backlight_val | 0x04, low_nibble | self.backlight_val]))
        time.sleep_ms(2)

    def send_char(self, char):
        """ Sending a character to the display """
        high_nibble = (char & 0xF0) | self.backlight_val | 0x05
        low_nibble = ((char << 4) & 0xF0) | self.backlight_val | 0x05
        self.i2c.writeto(self.addr, bytearray([high_nibble, high_nibble & 0xFB,
                                               low_nibble, low_nibble & 0xFB]))
        time.sleep_ms(2)

    def set_cursor(self, line, position):
        """ Setting the cursor to a position """
        address = 0x80 + (0x40 * (line - 1)) + position
        self.send_cmd(address)

    def write(self, text, line=1, position=0):
        """ Output text to a given line and position """
        self.set_cursor(line, position)
        for char in text:
            self.send_char(ord(char))

    def clear(self):
        """ CLear display """
        self.send_cmd(0x01)
        time.sleep_ms(2)

    def scroll_text_left(self, text, line, delay=0.3, repeat=1):
        """ Scroll text left on one line """
        padding = " " * self.display_width
        temp_text = text + padding
        for _ in range(repeat):
            for i in range(len(text) + 1):
                self.write(temp_text[i:i + self.display_width], line)
                time.sleep(delay)

    def scroll_text_right(self, text, line, delay=0.3, repeat=1):
        """ Scroll text right on one line """
        padding = " " * self.display_width
        temp_text = padding + text
        for _ in range(repeat):
            for i in range(len(text) + 1):
                self.write(temp_text[-(i + self.display_width):-i if -i != 0 else None], line)
                time.sleep(delay)

    def scroll_text_vertical(self, text, delay=0.5, repeat=1):
        """ Vertical scrolling of text on a two-line display """
        lines = [text[i:i + self.display_width] for i in range(0, len(text), self.display_width)]
        lines = [' ' * self.display_width] + lines + [' ' * self.display_width]
        for _ in range(repeat):
            for i in range(len(lines) - 1):
                self.write(lines[i], line=1)
                self.write(lines[i + 1], line=2)
                time.sleep(delay)

    def create_char(self, location, charmap):
        """
        Creates a custom symbol.
        location: memory location number for the symbol (0-7)
        charmap: a list of 8 bytes describing the character.
        """

        if location < 0 or location > 7:
            raise ValueError("The location must be between 0 and 7")
        self.send_cmd(0x40 + (location * 8))
        for i in range(8):
            self.send_char(charmap[i])
        self.send_cmd(0x80)

