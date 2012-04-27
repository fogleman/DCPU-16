import assembler
import wx
import wx.richtext as rt

COMMENT = (0, 128, 0)
OPCODE = (0, 64, 128)
OPERAND = (128, 0, 64)
LITERAL = (255, 0, 0)
STRING = (128, 128, 128)
SYMBOL = (0, 0, 0)
LABEL = (0, 0, 0)
ID = (0, 0, 0)
UNKNOWN = (255, 0, 110)

EVT_CONTROL_CHANGED = wx.PyEventBinder(wx.NewEventType())

class Event(wx.PyEvent):
    def __init__(self, event_object, event_type):
        super(Event, self).__init__()
        self.SetEventType(event_type.typeId)
        self.SetEventObject(event_object)

class Editor(rt.RichTextCtrl):
    def __init__(self, parent):
        super(Editor, self).__init__(parent, style=wx.WANTS_CHARS)
        self.post_events = True
        self.init_style()
        self.Bind(rt.EVT_RICHTEXT_CHARACTER, self.on_character)
        self.Bind(rt.EVT_RICHTEXT_CONTENT_DELETED, self.on_content_deleted)
        self.Bind(rt.EVT_RICHTEXT_CONTENT_INSERTED, self.on_content_inserted)
        self.Bind(rt.EVT_RICHTEXT_DELETE, self.on_delete)
        self.Bind(rt.EVT_RICHTEXT_RETURN, self.on_return)
    def post_event(self):
        if self.post_events:
            event = Event(self, EVT_CONTROL_CHANGED)
            wx.PostEvent(self, event)
    def set_value(self, value):
        self.post_events = False
        try:
            self.SetValue(value)
            self.colorize()
        finally:
            self.post_events = True
    def init_style(self):
        attr = rt.RichTextAttr()
        attr.SetFlags(
            rt.TEXT_ATTR_FONT_FACE |
            rt.TEXT_ATTR_FONT_SIZE)
        attr.SetFontFaceName('Courier New')
        attr.SetFontSize(10)
        self.SetBasicStyle(attr)
    def reset_style(self, start, end):
        attr = rt.RichTextAttr()
        attr.SetFlags(
            rt.TEXT_ATTR_TEXT_COLOUR |
            rt.TEXT_ATTR_FONT_WEIGHT)
        attr.SetTextColour(wx.Colour(*COMMENT))
        self.SetStyle(rt.RichTextRange(start, end), attr)
    def colorize(self, line=None):
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
            color = None
            bold = False
            if token.type in assembler.BASIC_OPCODES:
                color = OPCODE
                bold = True
            elif token.type in assembler.SPECIAL_OPCODES:
                color = OPCODE
                bold = True
            elif token.type == 'DAT':
                color = OPCODE
                bold = True
            elif token.type in assembler.REGISTERS:
                color = OPERAND
            elif token.type in assembler.SRC_CODES:
                color = OPERAND
            elif token.type in assembler.DST_CODES:
                color = OPERAND
            elif token.type == 'PICK':
                color = OPERAND
            elif token.type in ['DECIMAL', 'HEX', 'OCT']:
                color = LITERAL
            elif token.type in ['STRING', 'CHAR']:
                color = STRING
            elif token.type in ['INC', 'DEC', 'LBRACK', 'RBRACK', 'PLUS', 'AT']:
                color = SYMBOL
                bold = True
            elif token.type == 'LABEL':
                color = LABEL
            elif token.type == 'ID':
                color = ID
            else:
                color = UNKNOWN
            attr = rt.RichTextAttr()
            flags = 0
            if color:
                flags |= rt.TEXT_ATTR_TEXT_COLOUR
                attr.SetTextColour(wx.Colour(*color))
            if bold:
                flags |= rt.TEXT_ATTR_FONT_WEIGHT
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
        self.colorize(line)
        self.post_event()
    def on_content_deleted(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.colorize(line)
        self.colorize(line + 1)
        self.post_event()
    def on_content_inserted(self, event):
        event.Skip()
        start, end = event.GetRange()
        start = self.PositionToXY(start)[1]
        end = self.PositionToXY(end)[1]
        self.Freeze()
        for line in range(start, end + 1):
            self.colorize(line)
        self.Thaw()
        self.post_event()
    def on_delete(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.colorize(line)
        self.colorize(line + 1)
        self.post_event()
    def on_return(self, event):
        event.Skip()
        line = self.PositionToXY(event.GetPosition())[1]
        self.colorize(line)
        self.colorize(line + 1)
        self.post_event()
