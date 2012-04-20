import assembler
import emulator
import sys
import time
import wx

class Canvas(wx.Panel):
    def __init__(self, parent, emu):
        super(Canvas, self).__init__(parent)
        self.emu = emu
        self.colors = {
            0x0: wx.Colour(0x00, 0x00, 0x00),
            0x1: wx.Colour(0x00, 0x00, 0xaa),
            0x2: wx.Colour(0x00, 0xaa, 0x00),
            0x3: wx.Colour(0x00, 0xaa, 0xaa),
            0x4: wx.Colour(0xaa, 0x00, 0x00),
            0x5: wx.Colour(0xaa, 0x00, 0xaa),
            0x6: wx.Colour(0xaa, 0x55, 0x00),
            0x7: wx.Colour(0xaa, 0xaa, 0xaa),
            0x8: wx.Colour(0x55, 0x55, 0x55),
            0x9: wx.Colour(0x55, 0x55, 0xff),
            0xa: wx.Colour(0x55, 0xff, 0x55),
            0xb: wx.Colour(0x55, 0xff, 0xff),
            0xc: wx.Colour(0xff, 0x55, 0x55),
            0xd: wx.Colour(0xff, 0x55, 0xff),
            0xe: wx.Colour(0xff, 0xff, 0x55),
            0xf: wx.Colour(0xff, 0xff, 0xff),
        }
        self.scale = 4
        self.last_time = time.time()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        wx.CallAfter(self.on_timer)
    def update(self, dt):
        cycle = self.emu.cycle + int(dt * emulator.CYCLES_PER_SECOND)
        while self.emu.cycle < cycle:
            self.emu.step(False)
    def on_timer(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.update(dt)
        self.Refresh()
        wx.CallLater(15, self.on_timer)
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        self.draw_screen(dc)
    def draw_screen(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        address = 0x8000
        for j in xrange(12):
            for i in xrange(32):
                value = self.emu.ram[address]
                character = value & 0xff
                color = (value >> 8) & 0xff
                back = self.colors[color & 0x0f]
                fore = self.colors[(color >> 4) & 0x0f]
                left = self.emu.ram[0x8180 + character]
                right = self.emu.ram[0x8181 + character]
                bitmap = left << 16 | right
                x = i * 4 * self.scale
                y = j * 8 * self.scale
                dc.SetDeviceOrigin(x, y)
                self.draw_character(dc, back, fore, bitmap)
                address += 1
    def draw_character(self, dc, back, fore, bitmap):
        mask = 1
        for i in reversed(xrange(4)):
            for j in xrange(8):
                x = i * self.scale
                y = j * self.scale
                if bitmap & mask:
                    dc.SetBrush(wx.Brush(fore))
                else:
                    dc.SetBrush(wx.Brush(back))
                dc.DrawRectangle(x, y, self.scale, self.scale)
                mask <<= 1

def main(emu):
    app = wx.App(None)
    frame = wx.Frame(None)
    Canvas(frame, emu)
    frame.SetTitle('DCPU-16 Emulator')
    frame.SetClientSize((128 * 4, 96 * 4))
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
