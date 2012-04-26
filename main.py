import assembler
import emulator
import functools
import icons
import sys
import time
import wx

# Constants
SCALE = 3
WIDTH = 128
HEIGHT = 96
BORDER = 10
CYCLES_PER_SECOND = 100000
BLINK_RATE = 50000

FONT = [
    0xb79e, 0x388e, 0x722c, 0x75f4, 0x19bb, 0x7f8f, 0x85f9, 0xb158,
    0x242e, 0x2400, 0x082a, 0x0800, 0x0008, 0x0000, 0x0808, 0x0808,
    0x00ff, 0x0000, 0x00f8, 0x0808, 0x08f8, 0x0000, 0x080f, 0x0000,
    0x000f, 0x0808, 0x00ff, 0x0808, 0x08f8, 0x0808, 0x08ff, 0x0000,
    0x080f, 0x0808, 0x08ff, 0x0808, 0x6633, 0x99cc, 0x9933, 0x66cc,
    0xfef8, 0xe080, 0x7f1f, 0x0701, 0x0107, 0x1f7f, 0x80e0, 0xf8fe,
    0x5500, 0xaa00, 0x55aa, 0x55aa, 0xffaa, 0xff55, 0x0f0f, 0x0f0f,
    0xf0f0, 0xf0f0, 0x0000, 0xffff, 0xffff, 0x0000, 0xffff, 0xffff,
    0x0000, 0x0000, 0x005f, 0x0000, 0x0300, 0x0300, 0x3e14, 0x3e00,
    0x266b, 0x3200, 0x611c, 0x4300, 0x3629, 0x7650, 0x0002, 0x0100,
    0x1c22, 0x4100, 0x4122, 0x1c00, 0x1408, 0x1400, 0x081c, 0x0800,
    0x4020, 0x0000, 0x0808, 0x0800, 0x0040, 0x0000, 0x601c, 0x0300,
    0x3e49, 0x3e00, 0x427f, 0x4000, 0x6259, 0x4600, 0x2249, 0x3600,
    0x0f08, 0x7f00, 0x2745, 0x3900, 0x3e49, 0x3200, 0x6119, 0x0700,
    0x3649, 0x3600, 0x2649, 0x3e00, 0x0024, 0x0000, 0x4024, 0x0000,
    0x0814, 0x2200, 0x1414, 0x1400, 0x2214, 0x0800, 0x0259, 0x0600,
    0x3e59, 0x5e00, 0x7e09, 0x7e00, 0x7f49, 0x3600, 0x3e41, 0x2200,
    0x7f41, 0x3e00, 0x7f49, 0x4100, 0x7f09, 0x0100, 0x3e41, 0x7a00,
    0x7f08, 0x7f00, 0x417f, 0x4100, 0x2040, 0x3f00, 0x7f08, 0x7700,
    0x7f40, 0x4000, 0x7f06, 0x7f00, 0x7f01, 0x7e00, 0x3e41, 0x3e00,
    0x7f09, 0x0600, 0x3e61, 0x7e00, 0x7f09, 0x7600, 0x2649, 0x3200,
    0x017f, 0x0100, 0x3f40, 0x7f00, 0x1f60, 0x1f00, 0x7f30, 0x7f00,
    0x7708, 0x7700, 0x0778, 0x0700, 0x7149, 0x4700, 0x007f, 0x4100,
    0x031c, 0x6000, 0x417f, 0x0000, 0x0201, 0x0200, 0x8080, 0x8000,
    0x0001, 0x0200, 0x2454, 0x7800, 0x7f44, 0x3800, 0x3844, 0x2800,
    0x3844, 0x7f00, 0x3854, 0x5800, 0x087e, 0x0900, 0x4854, 0x3c00,
    0x7f04, 0x7800, 0x047d, 0x0000, 0x2040, 0x3d00, 0x7f10, 0x6c00,
    0x017f, 0x0000, 0x7c18, 0x7c00, 0x7c04, 0x7800, 0x3844, 0x3800,
    0x7c14, 0x0800, 0x0814, 0x7c00, 0x7c04, 0x0800, 0x4854, 0x2400,
    0x043e, 0x4400, 0x3c40, 0x7c00, 0x1c60, 0x1c00, 0x7c30, 0x7c00,
    0x6c10, 0x6c00, 0x4c50, 0x3c00, 0x6454, 0x4c00, 0x0836, 0x4100,
    0x0077, 0x0000, 0x4136, 0x0800, 0x0201, 0x0201, 0x0205, 0x0200,
]

PALETTE = [
    0x0000, 0x000a, 0x00a0, 0x00aa, 0x0a00, 0x0a0a, 0x0a50, 0x0aaa,
    0x0555, 0x055f, 0x05f5, 0x05ff, 0x0f55, 0x0f5f, 0x0ff5, 0x0fff,
]

KEYS = {
    wx.WXK_BACK: 0x10,
    wx.WXK_RETURN: 0x11,
    wx.WXK_INSERT: 0x12,
    wx.WXK_DELETE: 0x13,
    wx.WXK_UP: 0x80,
    wx.WXK_DOWN: 0x81,
    wx.WXK_LEFT: 0x82,
    wx.WXK_RIGHT: 0x83,
    wx.WXK_SHIFT: 0x90,
    wx.WXK_CONTROL: 0x91,
}

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
    if sys.platform == 'darwin':
        size = int(size * 1.5)
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

class Editor(wx.TextCtrl):
    def __init__(self, parent):
        style = wx.TE_MULTILINE | wx.TE_PROCESS_TAB | wx.TE_DONTWRAP
        super(Editor, self).__init__(parent, style=style)
        self.SetFont(make_font('Courier New', 9))
        self.Bind(wx.EVT_CHAR, self.on_char)
    def on_char(self, event):
        if event.GetKeyCode() == wx.WXK_TAB:
            self.WriteText('    ')
        else:
            event.Skip()

class Canvas(wx.Panel):
    def __init__(self, parent, emu):
        style = wx.WANTS_CHARS | wx.BORDER_STATIC
        super(Canvas, self).__init__(parent, style=style)
        self.emu = emu
        self.scale = 0
        self.cache = {}
        self.bitmap = wx.EmptyBitmap(1, 1)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_CHAR, self.on_char)
        self.SetInitialSize((
            WIDTH * SCALE + BORDER * 4,
            HEIGHT * SCALE + BORDER * 4 + 24))
    def on_key_down(self, event):
        event.Skip()
        code = event.GetKeyCode()
        code = KEYS.get(code, code)
        self.emu.on_key_down(code)
    def on_key_up(self, event):
        event.Skip()
        code = event.GetKeyCode()
        code = KEYS.get(code, code)
        self.emu.on_key_up(code)
    def on_char(self, event):
        event.Skip()
        code = event.GetKeyCode()
        code = KEYS.get(code, code)
        self.emu.on_char(code)
    def on_size(self, event):
        event.Skip()
        self.Refresh()
        cw, ch = self.GetClientSize()
        scale = min((cw - BORDER * 2) / WIDTH, (ch - BORDER * 2) / HEIGHT)
        scale = max(scale, 1)
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
        border_brush = self.draw_screen(mdc)
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(border_brush)
        dc.Clear()
        dc.Blit(dx, dy, bw, bh, mdc, 0, 0)
    def get_character(self, address, show_blink=True):
        value = self.emu.ram[address]
        character = value & 0x7f
        blink = bool(value & 0x80)
        color = (value >> 8) & 0xff
        back = color & 0x0f
        fore = (color >> 4) & 0x0f
        if blink and not show_blink:
            fore = back
        return character, back, fore
    def draw_screen(self, dc):
        address = self.emu.lem1802_screen
        if not address:
            self.cache = {}
            dc.SetBackground(wx.BLACK_BRUSH)
            dc.Clear()
            return wx.BLACK_BRUSH
        font_address = self.emu.lem1802_font
        if font_address:
            font = self.emu.ram[font_address : font_address + 256]
        else:
            font = FONT
        palette_address = self.emu.lem1802_palette
        if palette_address:
            palette = self.emu.ram[palette_address : palette_address + 16]
        else:
            palette = PALETTE
        brushes = []
        for x in palette:
            r, g, b = (x >> 8) & 0xf, (x >> 4) & 0xf, (x >> 0) & 0xf
            r, g, b = (r << 4) | r, (g << 4) | g, (b << 4) | b
            brushes.append(wx.Brush(wx.Colour(r, g, b)))
        dc.SetPen(wx.TRANSPARENT_PEN)
        show_blink = bool((self.emu.cycle / BLINK_RATE) % 2)
        for j in xrange(12):
            for i in xrange(32):
                ch, back, fore = self.get_character(address, show_blink)
                a = font[ch * 2]
                b = font[ch * 2 + 1]
                bitmap = a << 16 | b
                key = (palette[back], palette[fore], bitmap)
                if self.cache.get((i, j)) != key:
                    self.cache[(i, j)] = key
                    x, y = i * 4 * self.scale, j * 8 * self.scale
                    self.draw_character(dc, x, y, brushes[back],
                        brushes[fore], bitmap)
                address += 1
        return brushes[self.emu.lem1802_border & 0xf]
    def draw_character(self, dc, x, y, back, fore, bitmap):
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
        self.program = None
        self.running = False
        self.step_power = 0
        self.refresh_rate = 1
        self.cycles_per_second = CYCLES_PER_SECOND
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
        menu_item(self, menu, 'New\tCtrl+N', self.on_new)
        menu_item(self, menu, 'Open...\tCtrl+O', self.on_open)
        menu_item(self, menu, 'Save As...\tCtrl+S', self.on_save_as)
        menu_item(self, menu, 'Save Binary...\tCtrl+D', self.on_save_binary)
        menu.AppendSeparator()
        menu_item(self, menu, 'Exit\tAlt+F4', self.on_exit)
        menubar.Append(menu, '&File')
        # Edit
        menu = wx.Menu()
        menu_item(self, menu, 'Select All\tCtrl+A', self.on_select_all)
        menubar.Append(menu, '&Edit')
        # Run
        menu = wx.Menu()
        menu_item(self, menu, 'Assemble\tF4', self.on_assemble)
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
        menu.AppendSeparator()
        for power in range(-2, 6):
            func = functools.partial(self.on_clock_rate, power=power)
            item = menu_item(self, menu, '%gx Clock Rate' % (2 ** power), func,
                wx.ITEM_RADIO)
            if power == 0:
                item.Check()
        menubar.Append(menu, '&Run')
        # View
        menu = wx.Menu()
        item = menu_item(self, menu, 'Show Debug Controls\tF12',
            self.on_toggle_debug, wx.ITEM_CHECK)
        item.Check()
        menu.AppendSeparator()
        data = [
            (-1, 'No Refresh'),
            (0, 'Live Refresh'),
            (1, 'One Second Refresh'),
        ]
        for rate, name in data:
            func = functools.partial(self.on_refresh_rate, rate=rate)
            item = menu_item(self, menu, name, func, wx.ITEM_RADIO)
            if rate == self.refresh_rate:
                item.Check()
        menubar.Append(menu, '&View')
        self.SetMenuBar(menubar)
    def create_toolbar(self):
        style = wx.HORIZONTAL | wx.TB_FLAT | wx.TB_NODIVIDER
        toolbar = self.CreateToolBar(style)
        toolbar.SetToolBitmapSize((18, 18))
        tool_item(self, toolbar, 'New', self.on_new, icons.page)
        tool_item(self, toolbar, 'Open', self.on_open, icons.folder_page)
        toolbar.AddSeparator()
        tool_item(self, toolbar, 'Assemble', self.on_assemble, icons.basket_put)
        tool_item(self, toolbar, 'Start', self.on_start, icons.control_play)
        tool_item(self, toolbar, 'Stop', self.on_stop, icons.control_stop)
        tool_item(self, toolbar, 'Step', self.on_step, icons.control_end)
        toolbar.Realize()
        toolbar.Fit()
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
    def reset(self):
        self.running = False
        self.program = None
        self.emu.reset()
        self.program_list.update([])
        self.refresh_debug_info()
    def on_new(self, event):
        self.reset()
        self.editor.SetValue('')
    def open_file(self, path):
        try:
            self.reset()
            self.program = assembler.open_file(path)
            self.emu.load(self.program.assemble())
            self.program_list.update(self.program.instructions)
            self.editor.SetValue(self.program.text)
            self.refresh_debug_info()
        except Exception as e:
            self.reset()
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
    def on_save_as(self, event):
        dialog = wx.FileDialog(self, 'Save As', wildcard='*.dasm',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            with open(path, 'w') as fp:
                fp.write(self.editor.GetValue())
        dialog.Destroy()
    def save_binary(self, path):
        words = self.program.assemble()
        data = []
        for word in words:
            data.append(chr((word >> 8) & 0xff))
            data.append(chr((word >> 0) & 0xff))
        data = ''.join(data)
        with open(path, 'wb') as fp:
            fp.write(data)
    def on_save_binary(self, event):
        if self.program is None:
            return
        dialog = wx.FileDialog(self, 'Save Binary', wildcard='*.obj',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            self.save_binary(path)
        dialog.Destroy()
    def on_select_all(self, event):
        self.editor.SelectAll()
    def on_exit(self, event):
        self.Close()
    def assemble(self):
        text = self.editor.GetValue()
        try:
            self.reset()
            self.program = assembler.parse(text)
            self.emu.load(self.program.assemble())
            self.program_list.update(self.program.instructions)
            self.refresh_debug_info()
        except Exception as e:
            self.reset()
            dialog = wx.MessageDialog(self, str(e), 'Error',
                wx.ICON_ERROR | wx.OK)
            dialog.ShowModal()
            dialog.Destroy()
    def on_assemble(self, event):
        self.assemble()
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
    def on_clock_rate(self, event, power):
        self.cycles_per_second = CYCLES_PER_SECOND * (2 ** power)
    def on_toggle_debug(self, event):
        self.show_debug = not self.show_debug
        self.show_debug_controls(self.show_debug)
    def on_refresh_rate(self, event, rate):
        self.refresh_rate = rate
    def on_page_changed(self, event):
        event.Skip()
        index = event.GetEventObject().GetSelection()
        if index == 0:
            wx.CallAfter(self.editor.SetFocus)
        else:
            wx.CallAfter(self.canvas.SetFocus)
    def update(self, dt):
        if self.running:
            cycles = int(dt * self.cycles_per_second)
            self.emu.n_cycles(cycles)
    def refresh(self):
        self.canvas.Refresh()
        self.canvas.Update()
        if self.running and self.refresh_rate >= 0:
            if time.time() - self.last_refresh > self.refresh_rate:
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
        notebook = self.create_notebook(parent)
        registers = self.create_registers(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND)
        c1 = sizer.AddSpacer(10)
        c2 = sizer.Add(registers, 0, wx.EXPAND)
        self.debug_controls.extend([c1, c2])
        return sizer
    def create_notebook(self, parent):
        notebook = wx.Notebook(parent)
        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        editor = self.create_editor(notebook)
        canvas = self.create_canvas(notebook)
        notebook.AddPage(editor, 'Editor')
        notebook.AddPage(canvas, 'Display')
        return notebook
    def create_editor(self, parent):
        panel = wx.Panel(parent)
        self.editor = Editor(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.editor, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        return panel
    def create_canvas(self, parent):
        panel = wx.Panel(parent)
        self.canvas = Canvas(panel, self.emu)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)
        return panel
    def create_registers(self, parent):
        self.registers = {}
        sizer = wx.FlexGridSizer(4, 6, 5, 5)
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
            ('EX', 10),
            ('IA', 11),
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
