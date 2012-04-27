import assembler
import sys
import wx
import wx.richtext as rt

# Styles
class Style(object):
    def __init__(self, color, bold=False):
        self.color = wx.Colour(*color)
        self.bold = bold

COMMENT = Style((0, 128, 0))
OPCODE = Style((0, 64, 128), True)
OPERAND = Style((128, 0, 64))
LITERAL = Style((255, 0, 0))
STRING = Style((128, 128, 128))
SYMBOL = Style((0, 0, 0), True)
LABEL = Style((0, 0, 0))
ID = Style((0, 0, 0))
UNKNOWN = Style((255, 0, 110))

# Events
class Event(wx.PyEvent):
    def __init__(self, event_object, event_type):
        super(Event, self).__init__()
        self.SetEventType(event_type.typeId)
        self.SetEventObject(event_object)

EVT_CONTROL_CHANGED = wx.PyEventBinder(wx.NewEventType())

# Editor Control
class Editor(rt.RichTextCtrl):
    def __init__(self, parent):
        super(Editor, self).__init__(parent, style=wx.WANTS_CHARS)
        self.post_events = True
        self.styles = self.build_styles()
        self.init_style()
        self.Bind(rt.EVT_RICHTEXT_CHARACTER, self.on_character)
        self.Bind(rt.EVT_RICHTEXT_CONTENT_DELETED, self.on_content_deleted)
        self.Bind(rt.EVT_RICHTEXT_CONTENT_INSERTED, self.on_content_inserted)
        self.Bind(rt.EVT_RICHTEXT_DELETE, self.on_delete)
        self.Bind(rt.EVT_RICHTEXT_RETURN, self.on_return)
    def build_styles(self):
        result = {}
        for name in assembler.BASIC_OPCODES:
            result[name] = OPCODE
        for name in assembler.SPECIAL_OPCODES:
            result[name] = OPCODE
        for name in ['DAT']:
            result[name] = OPCODE
        for name in assembler.REGISTERS:
            result[name] = OPERAND
        for name in assembler.SRC_CODES:
            result[name] = OPERAND
        for name in assembler.DST_CODES:
            result[name] = OPERAND
        for name in ['PICK']:
            result[name] = OPERAND
        for name in ['DECIMAL', 'HEX', 'OCT']:
            result[name] = LITERAL
        for name in ['STRING', 'CHAR']:
            result[name] = STRING
        for name in ['INC', 'DEC', 'LBRACK', 'RBRACK', 'PLUS', 'AT']:
            result[name] = SYMBOL
        for name in ['LABEL']:
            result[name] = LABEL
        for name in ['ID']:
            result[name] = ID
        return result
    def post_event(self):
        if self.post_events:
            event = Event(self, EVT_CONTROL_CHANGED)
            wx.PostEvent(self, event)
    def set_value(self, value):
        self.post_events = False
        try:
            self.SetValue(value)
        finally:
            self.post_events = True
        self.stylize()
    def init_style(self):
        size = 10
        if sys.platform == 'darwin':
            size = int(size * 1.5)
        attr = rt.RichTextAttr()
        attr.SetFlags(
            wx.TEXT_ATTR_FONT_FACE |
            wx.TEXT_ATTR_FONT_SIZE)
        attr.SetFontFaceName('Courier New')
        attr.SetFontSize(size)
        self.SetBasicStyle(attr)
    def reset_style(self, start, end):
        attr = rt.RichTextAttr()
        attr.SetFlags(
            wx.TEXT_ATTR_TEXT_COLOUR |
            wx.TEXT_ATTR_FONT_WEIGHT)
        attr.SetTextColour(COMMENT.color)
        self.SetStyle(rt.RichTextRange(start, end), attr)
    def stylize(self, line=None):
        if not self.post_events:
            return
        if line is None:
            text = self.GetValue()
            offset = 0
        else:
            text = self.GetLineText(line)
            offset = self.XYToPosition(0, line)
        lexer = assembler.LEXER
        lexer.input(text)
        self.Freeze()
        self.BeginSuppressUndo()
        self.reset_style(offset, offset + len(text))
        while True:
            try:
                token = lexer.token()
            except Exception:
                break
            if token is None:
                break
            start = offset + token.lexpos
            end = offset + lexer.lexpos
            rng = rt.RichTextRange(start, end)
            style = self.styles.get(token.type, UNKNOWN)
            attr = rt.RichTextAttr()
            flags = wx.TEXT_ATTR_TEXT_COLOUR
            attr.SetTextColour(style.color)
            if style.bold:
                flags |= wx.TEXT_ATTR_FONT_WEIGHT
                attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            attr.SetFlags(flags)
            self.SetStyle(rng, attr)
        self.EndSuppressUndo()
        self.Thaw()
    def on_character(self, event):
        event.Skip()
        if event.GetCharacter() == '\t':
            pos = event.GetPosition()
            self.Remove(pos, pos)
            self.WriteText('    ')
        line = self.PositionToXY(event.GetPosition())[1]
        self.stylize(line)
        self.post_event()
    def on_content_deleted(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.stylize(line)
        self.stylize(line + 1)
        self.post_event()
    def on_content_inserted(self, event):
        event.Skip()
        start, end = event.GetRange()
        start = self.PositionToXY(start)[1]
        end = self.PositionToXY(end)[1]
        self.Freeze()
        for line in range(start, end + 1):
            self.stylize(line)
        self.Thaw()
        self.post_event()
    def on_delete(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.stylize(line)
        self.stylize(line + 1)
        self.post_event()
    def on_return(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.stylize(line)
        self.stylize(line + 1)
        self.post_event()
