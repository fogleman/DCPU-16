import assembler
import emulator
import sys
import time
import wx

SCALE = 4
BORDER = 10

class Canvas(wx.Panel):
    def __init__(self, parent, emu):
        super(Canvas, self).__init__(parent, style=wx.WANTS_CHARS)
        self.emu = emu
        self.brushes = {
            0x0: wx.Brush(wx.Colour(0x00, 0x00, 0x00)),
            0x1: wx.Brush(wx.Colour(0x00, 0x00, 0xaa)),
            0x2: wx.Brush(wx.Colour(0x00, 0xaa, 0x00)),
            0x3: wx.Brush(wx.Colour(0x00, 0xaa, 0xaa)),
            0x4: wx.Brush(wx.Colour(0xaa, 0x00, 0x00)),
            0x5: wx.Brush(wx.Colour(0xaa, 0x00, 0xaa)),
            0x6: wx.Brush(wx.Colour(0xaa, 0x55, 0x00)),
            0x7: wx.Brush(wx.Colour(0xaa, 0xaa, 0xaa)),
            0x8: wx.Brush(wx.Colour(0x55, 0x55, 0x55)),
            0x9: wx.Brush(wx.Colour(0x55, 0x55, 0xff)),
            0xa: wx.Brush(wx.Colour(0x55, 0xff, 0x55)),
            0xb: wx.Brush(wx.Colour(0x55, 0xff, 0xff)),
            0xc: wx.Brush(wx.Colour(0xff, 0x55, 0x55)),
            0xd: wx.Brush(wx.Colour(0xff, 0x55, 0xff)),
            0xe: wx.Brush(wx.Colour(0xff, 0xff, 0x55)),
            0xf: wx.Brush(wx.Colour(0xff, 0xff, 0xff)),
        }
        self.key_index = 0
        self.bitmap = wx.EmptyBitmap(1, 1)
        self.cache = {}
        self.scale = SCALE
        self.last_time = time.time()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_CHAR, self.on_char)
        wx.CallAfter(self.on_timer)
    def update(self, dt):
        cycle = self.emu.cycle + int(dt * emulator.CYCLES_PER_SECOND)
        while self.emu.cycle < cycle:
            self.emu.step(False)
    def on_char(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            code = 0x0a
        else:
            code = event.GetUniChar()
        self.emu.ram[0x9000 + self.key_index] = code
        self.emu.ram[0x9010] = self.key_index
        self.key_index = (self.key_index + 1) % 16
    def on_timer(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.update(dt)
        self.Refresh()
        wx.CallLater(5, self.on_timer)
    def on_size(self, event):
        event.Skip()
        w, h = self.GetClientSize()
        self.bitmap = wx.EmptyBitmap(w, h)
        self.cache = {}
        self.Refresh()
    def on_paint(self, event):
        bitmap = self.bitmap
        mdc = wx.MemoryDC(bitmap)
        self.draw_screen(mdc)
        dc = wx.AutoBufferedPaintDC(self)
        dc.Blit(0, 0, bitmap.GetWidth(), bitmap.GetHeight(), mdc, 0, 0)
    def draw_screen(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        address = 0x8000
        for j in xrange(12):
            for i in xrange(32):
                value = self.emu.ram[address]
                character = value & 0xff
                color = (value >> 8) & 0xff
                back = color & 0x0f
                fore = (color >> 4) & 0x0f
                a = self.emu.ram[0x8180 + character * 2]
                b = self.emu.ram[0x8181 + character * 2]
                bitmap = a << 16 | b
                key = (back, fore, bitmap)
                if self.cache.get((i, j)) != key:
                    self.cache[(i, j)] = key
                    x = i * 4 * self.scale + BORDER
                    y = j * 8 * self.scale + BORDER
                    self.draw_character(dc, x, y, back, fore, bitmap)
                address += 1
    def draw_character(self, dc, x, y, back, fore, bitmap):
        back = self.brushes[back]
        fore = self.brushes[fore]
        mask = 1
        for i in xrange(3, -1, -1):
            for j in xrange(8):
                dx = i * self.scale
                dy = j * self.scale
                if bitmap & mask:
                    dc.SetBrush(fore)
                else:
                    dc.SetBrush(back)
                dc.DrawRectangle(x + dx, y + dy, self.scale, self.scale)
                mask <<= 1

def main(emu):
    app = wx.App(None)
    style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
    frame = wx.Frame(None, style=style)
    Canvas(frame, emu)
    frame.SetTitle('DCPU-16 Emulator')
    frame.SetClientSize((128 * SCALE + BORDER * 2, 96 * SCALE + BORDER * 2))
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 1:
        emu = emulator.Emulator()
        emu.load(assembler.assemble_file(args[0]))
        main(emu)
    else:
        print 'Usage: python display.py input.dasm'
