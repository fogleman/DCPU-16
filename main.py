from app import Emulator, Frame
import wx

def main():
    app = wx.App(None)
    frame = Frame(Emulator())
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
