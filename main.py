import assembler
import emulator
import functools
import icons
import sys
import time
import wx

# Select C or Python Emulator
try:
    import cEmulator
except Exception:
    cEmulator = None

emulator = cEmulator or emulator

# Constants
SCALE = 3
WIDTH = 128
HEIGHT = 96
BORDER = 10
CYCLES_PER_SECOND = 100000
BLINK_RATE = 50000

# Helper Functions
def menu_item(window, menu, label, func, kind=wx.ITEM_NORMAL):
    item = wx.MenuItem(menu, -1, label, '', kind)
    window.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

def tool_item(window, toolbar, label, func, icon):
    item = toolbar.AddSimpleTool(-1, icon.GetBitmap(), label)
    window.Bind(wx.EVT_TOOL, func, id=item.GetId())
    return item

def make_font(face, size, bold=False, italic=False, underline=False):
    family = wx.FONTFAMILY_DEFAULT
    style = wx.FONTSTYLE_ITALIC if italic else wx.FONTSTYLE_NORMAL
    weight = wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL
    font = wx.Font(size, family, style, weight, underline, face)
    return font

def set_icon(window):
    bundle = wx.IconBundle()
    bundle.AddIcon(wx.IconFromBitmap(icons.icon16.GetBitmap()))
    bundle.AddIcon(wx.IconFromBitmap(icons.icon32.GetBitmap()))
    window.SetIcons(bundle)

# Controls
class RamList(wx.ListCtrl):
    INDEX_ADDR = 0
    INDEX_HEX = 1
    INDEX_DEC = 2
    def __init__(self, parent, emu):
        style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_SINGLE_SEL
        super(RamList, self).__init__(parent, -1, style=style)
        self.emu = emu
        self.InsertColumn(RamList.INDEX_ADDR, 'Addr')
        self.InsertColumn(RamList.INDEX_HEX, 'Hex')
        self.InsertColumn(RamList.INDEX_DEC, 'Dec')
        self.SetColumnWidth(RamList.INDEX_ADDR, 55)
        self.SetColumnWidth(RamList.INDEX_HEX, 55)
        self.SetColumnWidth(RamList.INDEX_DEC, 55)
        self.SetItemCount(0x10000)
        self.SetFont(make_font('Courier New', 9))
    def OnGetItemText(self, index, column):
        if column == RamList.INDEX_ADDR:
            return '%04x' % index
        if column == RamList.INDEX_HEX:
            return '%04x' % self.emu.ram[index]
        if column == RamList.INDEX_DEC:
            return '%d' % self.emu.ram[index]
        return ''

class ProgramList(wx.ListCtrl):
    INDEX_ADDR = 0
    INDEX_CODE = 1
    def __init__(self, parent):
        style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_SINGLE_SEL
        super(ProgramList, self).__init__(parent, -1, style=style)
        self.instructions = []
        self.lookup = {}
        self.InsertColumn(ProgramList.INDEX_ADDR, 'Addr')
        self.InsertColumn(ProgramList.INDEX_CODE, 'Code')
        self.SetColumnWidth(ProgramList.INDEX_ADDR, 55)
        self.SetColumnWidth(ProgramList.INDEX_CODE, 155)
        self.SetFont(make_font('Courier New', 9))
    def update(self, instructions):
        self.instructions = instructions
        self.lookup = {}
        for index, instruction in enumerate(instructions):
            self.lookup[instruction.offset] = index
        self.SetItemCount(len(instructions))
    def focus(self, offset):
        if offset not in self.lookup:
            return
        index = self.lookup[offset]
        self.Select(index)
        self.EnsureVisible(index)
    def OnGetItemText(self, index, column):
        instruction = self.instructions[index]
        if column == ProgramList.INDEX_ADDR:
            return '%04x' % instruction.offset
        if column == ProgramList.INDEX_CODE:
            return instruction.pretty(None).strip()
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
            HEIGHT * SCALE + BORDER * 4 + 24))
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
        show_blink = bool((self.emu.cycle / BLINK_RATE) % 2)
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
        self.last_refresh = time.time()
        self.running = False
        self.step_power = 0
        self.show_debug = True
        self.debug_controls = []
        set_icon(self)
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.panel = wx.Panel(self)
        sizer = self.create_controls(self.panel)
        self.panel.SetSizerAndFit(sizer)
        self.Fit()
        self.SetTitle('DCPU-16 Emulator')
        wx.CallAfter(self.on_timer)
        args = sys.argv[1:]
        if len(args) == 1:
            self.open_file(args[0])
    def create_menu(self):
        menubar = wx.MenuBar()
        # File
        menu = wx.Menu()
        menu_item(self, menu, 'Reset\tCtrl+N', self.on_reset)
        menu_item(self, menu, 'Open...\tCtrl+O', self.on_open)
        menu.AppendSeparator()
        menu_item(self, menu, 'Exit\tAlt+F4', self.on_exit)
        menubar.Append(menu, '&File')
        # Run
        menu = wx.Menu()
        menu_item(self, menu, 'Start\tF5', self.on_start)
        menu_item(self, menu, 'Stop\tF6', self.on_stop)
        menu_item(self, menu, 'Step\tF7', self.on_step)
        menu.AppendSeparator()
        for power in range(6):
            func = functools.partial(self.on_step_power, power=power)
            item = menu_item(self, menu, '10^%d Steps' % power, func,
                wx.ITEM_RADIO)
            if power == 0:
                item.Check()
        menubar.Append(menu, '&Run')
        # View
        menu = wx.Menu()
        item = menu_item(self, menu, 'Show Debug Controls',
            self.on_toggle_debug, wx.ITEM_CHECK)
        item.Check()
        menubar.Append(menu, '&View')
        self.SetMenuBar(menubar)
    def create_toolbar(self):
        style = wx.HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER
        toolbar = wx.ToolBar(self, style=style)
        toolbar.SetToolBitmapSize((18, 18))
        tool_item(self, toolbar, 'Reset', self.on_reset, icons.page)
        tool_item(self, toolbar, 'Open', self.on_open, icons.folder_page)
        toolbar.AddSeparator()
        tool_item(self, toolbar, 'Start', self.on_start, icons.control_play)
        tool_item(self, toolbar, 'Stop', self.on_stop, icons.control_stop)
        tool_item(self, toolbar, 'Step', self.on_step, icons.control_end)
        toolbar.Realize()
        toolbar.Fit()
        self.SetToolBar(toolbar)
    def create_statusbar(self):
        sizes = [0, 100, 140, -1]
        styles = [wx.SB_NORMAL] * len(sizes)
        styles[0] = wx.SB_FLAT
        bar = self.CreateStatusBar()
        bar.SetFieldsCount(len(sizes))
        bar.SetStatusWidths(sizes)
        bar.SetStatusStyles(styles)
        self.update_statusbar()
    def update_statusbar(self):
        bar = self.GetStatusBar()
        running = 'Running' if self.running else 'Not Running'
        bar.SetStatusText(running, 1)
        cycle = 'Cycle: %d' % self.emu.cycle
        bar.SetStatusText(cycle, 2)
    def show_debug_controls(self, show):
        for item in self.debug_controls:
            item.Show(show)
        self.panel.Layout()
    def on_reset(self, event):
        self.running = False
        self.emu.reset()
        self.program_list.update([])
        self.refresh_debug_info()
    def open_file(self, path):
        try:
            program = assembler.parse_file(path)
            self.emu.load(program.assemble())
            self.program_list.update(program.instructions)
            self.refresh_debug_info()
        except Exception as e:
            self.emu.reset()
            dialog = wx.MessageDialog(self, str(e), 'Error',
                wx.ICON_ERROR | wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
    def on_open(self, event):
        dialog = wx.FileDialog(self, 'Open',
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.open_file(path)
        dialog.Destroy()
    def on_exit(self, event):
        self.Close()
    def on_start(self, event):
        self.running = True
        self.refresh_debug_info()
    def on_stop(self, event):
        self.running = False
        self.refresh_debug_info()
    def on_step(self, event):
        steps = 10 ** self.step_power
        self.emu.n_steps(steps)
        self.refresh_debug_info()
    def on_step_power(self, event, power):
        self.step_power = power
    def on_toggle_debug(self, event):
        self.show_debug = not self.show_debug
        self.show_debug_controls(self.show_debug)
    def update(self, dt):
        if self.running:
            cycles = int(dt * CYCLES_PER_SECOND)
            self.emu.n_cycles(cycles)
    def refresh(self):
        self.canvas.Refresh()
        self.canvas.Update()
        if self.running and time.time() - self.last_refresh > 1:
            self.refresh_debug_info()
    def refresh_debug_info(self):
        self.last_refresh = time.time()
        self.update_statusbar()
        self.program_list.focus(self.emu.ram[0x10009])
        self.ram_list.RefreshItems(0, self.ram_list.GetItemCount() - 1)
        for address, widget in self.registers.iteritems():
            widget.SetValue('%04x' % self.emu.ram[address])
    def on_timer(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        self.update(dt)
        self.refresh()
        wx.CallLater(10, self.on_timer)
    def create_controls(self, parent):
        body = self.create_body(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(body, 1, wx.EXPAND | wx.ALL, 10)
        return sizer
    def create_body(self, parent):
        self.program_list = ProgramList(parent)
        self.program_list.SetInitialSize((245, -1))
        center = self.create_center(parent)
        self.ram_list = RamList(parent, self.emu)
        self.ram_list.SetInitialSize((200, -1))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        c1 = sizer.Add(self.program_list, 0, wx.EXPAND)
        c2 = sizer.AddSpacer(10)
        sizer.Add(center, 1, wx.EXPAND)
        c3 = sizer.AddSpacer(10)
        c4 = sizer.Add(self.ram_list, 0, wx.EXPAND)
        self.debug_controls.extend([c1, c2, c3, c4])
        return sizer
    def create_center(self, parent):
        self.canvas = Canvas(parent, self.emu)
        registers = self.create_registers(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        c1 = sizer.AddSpacer(10)
        c2 = sizer.Add(registers, 0, wx.EXPAND)
        self.debug_controls.extend([c1, c2])
        return sizer
    def create_registers(self, parent):
        self.registers = {}
        self.register_sizer = sizer = wx.FlexGridSizer(4, 6, 5, 5)
        for col in range(6):
            sizer.AddGrowableCol(col, 1)
        data1 = [
            ('A', 0),
            ('B', 1),
            ('C', 2),
            ('X', 3),
            ('Y', 4),
            ('Z', 5),
        ]
        data2 = [
            ('SP', 8),
            ('PC', 9),
            ('O', 10),
            ('LT', 11),
            ('I', 6),
            ('J', 7),
        ]
        groups = [data1, data2]
        for data in groups:
            for name, offset in data:
                text = wx.StaticText(parent, -1, name)
                sizer.Add(text, flag=wx.ALIGN_CENTER)
            for name, offset in data:
                address = 0x10000 + offset
                style = wx.TE_CENTER | wx.TE_READONLY
                size = (0, -1)
                text = wx.TextCtrl(parent, -1, '0000', size=size, style=style)
                text.SetFont(make_font('Courier New', 9))
                sizer.Add(text, 1, wx.EXPAND)
                self.registers[address] = text
        return sizer

# Main
def main():
    app = wx.App(None)
    frame = Frame(emulator.Emulator())
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
