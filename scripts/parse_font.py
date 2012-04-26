import wx

def main():
    _app = wx.App(None)
    result = []
    image = wx.ImageFromBitmap(wx.Bitmap('font.png'))
    for row in range(4):
        for col in range(32):
            value = 0
            mask = 1
            for i in range(3, -1, -1):
                for j in range(8):
                    x = col * 4 + i
                    y = row * 8 + j
                    on = image.GetRed(x, y) > 128
                    if on:
                        value |= mask
                    mask <<= 1
            a = (value >> 16) & 0xffff
            b = value & 0xffff
            result.append(a)
            result.append(b)
    return result

if __name__ == '__main__':
    data = main()
    while data:
        row = data[:8]
        del data[:8]
        print '    %s,' % ', '.join('0x%04x' % x for x in row)
