import assembler
import emulator
import sys
import time
import wx

try:
    import cEmulator
except Exception:
    cEmulator = None

emulator = cEmulator or emulator

SCALE = 4
WIDTH = 128
HEIGHT = 96
BORDER = 10
CYCLES_PER_SECOND = 100000

class RamList(wx.ListCtrl):
    INDEX_ADDR = 0
    INDEX_HEX = 1
    INDEX_DEC = 2
    def __init__(self, parent, emu):
        style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_SINGLE_SEL
        super(RamList, self).__init__(parent, -1, style=style)
        self.emu = emu
        self.InsertColumn(RamList.INDEX_ADDR, 'Index')
        self.InsertColumn(RamList.INDEX_HEX, 'Hex')
        self.InsertColumn(RamList.INDEX_DEC, 'Dec')
        self.SetColumnWidth(RamList.INDEX_ADDR, 64)
        self.SetColumnWidth(RamList.INDEX_HEX, 64)
        self.SetColumnWidth(RamList.INDEX_DEC, 64)
        self.SetItemCount(0x1000c)
    def OnGetItemText(self, index, column):
        if column == RamList.INDEX_ADDR:
            return '%04x' % index
        if column == RamList.INDEX_HEX:
            return '%04x' % self.emu.ram[index]
        if column == RamList.INDEX_DEC:
            return '%d' % self.emu.ram[index]
        return ''

class Canvas(wx.Panel):
    def __init__(self, parent, emu):
        style = wx.WANTS_CHARS | wx.BORDER_DOUBLE
        super(Canvas, self).__init__(parent, style=style)
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
        self.scale = 0
        self.cache = {}
        self.bitmap = wx.EmptyBitmap(1, 1)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.SetInitialSize((
            WIDTH * SCALE + BORDER * 4,
            HEIGHT * SCALE + BORDER * 4))
    def on_char(self, event):
        lookup = {
            wx.WXK_LEFT: 0x25,
            wx.WXK_UP: 0x26,
            wx.WXK_RIGHT: 0x27,
            wx.WXK_DOWN: 0x28,
            wx.WXK_RETURN: 0x0a,
        }
        code = lookup.get(event.GetKeyCode(), event.GetUniChar())
        for address in xrange(0x9000, 0x9010):
            if not self.emu.ram[address]:
                self.emu.ram[address] = code
                self.emu.ram[0x9010] = address
                break
    def on_size(self, event):
        event.Skip()
        self.Refresh()
        cw, ch = self.GetClientSize()
        scale = min((cw - BORDER * 2) / WIDTH, (ch - BORDER * 2) / HEIGHT) or 1
        if scale != self.scale:
            self.scale = scale
            self.cache = {}
            self.bitmap = wx.EmptyBitmap(WIDTH * scale, HEIGHT * scale)
            dc = wx.MemoryDC(self.bitmap)
            dc.SetBackground(wx.BLACK_BRUSH)
            dc.Clear()
    def on_paint(self, event):
        bitmap = self.bitmap
        cw, ch = self.GetClientSize()
        bw, bh = bitmap.GetWidth(), bitmap.GetHeight()
        dx, dy = (cw - bw) / 2, (ch - bh) / 2
        mdc = wx.MemoryDC(bitmap)
        self.draw_screen(mdc)
        dc = wx.AutoBufferedPaintDC(self)
        brush = self.brushes[self.get_character(0x8280)[1]]
        dc.SetBackground(brush)
        dc.Clear()
        dc.Blit(dx, dy, bw, bh, mdc, 0, 0)
    def get_character(self, address, show_blink=True):
        value = self.emu.ram[address]
        character = value & 0x7f
        blink = bool(value & 0x80)
        color = (value >> 8) & 0xff
        back = color & 0x0f
        fore = (color >> 4) & 0x0f
        a = self.emu.ram[0x8180 + character * 2]
        b = self.emu.ram[0x8181 + character * 2]
        bitmap = a << 16 | b
        if blink and not show_blink:
            fore = back
        return bitmap, back, fore
    def draw_screen(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        address = 0x8000
        show_blink = bool(int(time.time() * 2) % 2)
        for j in xrange(12):
            for i in xrange(32):
                bitmap, back, fore = self.get_character(address, show_blink)
                key = (back, fore, bitmap)
                if self.cache.get((i, j)) != key:
                    self.cache[(i, j)] = key
                    x = i * 4 * self.scale
                    y = j * 8 * self.scale
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

class Frame(wx.Frame):
    def __init__(self, emu):
        super(Frame, self).__init__(None)
        self.emu = emu
        self.last_time = time.time()
        panel = wx.Panel(self)
        sizer = self.create_controls(panel)
        panel.SetSizerAndFit(sizer)
        self.Fit()
        self.SetTitle('DCPU-16 Emulator')
        wx.CallAfter(self.on_timer)
    def update(self, dt):
        cycles = int(dt * CYCLES_PER_SECOND)
        self.emu.n_cycles(cycles)
    def on_timer(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.update(dt)
        #self.ram_list.RefreshItems(0, self.ram_list.GetItemCount() - 1)
        self.canvas.Refresh()
        self.canvas.Update()
        wx.CallLater(10, self.on_timer)
    def create_controls(self, parent):
        body = self.create_body(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(body, 1, wx.EXPAND | wx.ALL, 10)
        return sizer
    def create_body(self, parent):
        self.canvas = Canvas(parent, self.emu)
        #self.ram_list = RamList(parent, self.emu)
        #self.ram_list.SetInitialSize((220, -1))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        #sizer.AddSpacer(10)
        #sizer.Add(self.ram_list, 0, wx.EXPAND)
        return sizer

def main(emu):
    app = wx.App(None)
    frame = Frame(emu)
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
