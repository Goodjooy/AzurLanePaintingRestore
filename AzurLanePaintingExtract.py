from os import path
from sys import argv

import wx

import Classes.FrameClasses


def main_part(info):
    app = wx.App(False)
    frame = Classes.FrameClasses.MainFrame(None, info)
    frame.Show()

    app.MainLoop()


if __name__ == '__main__':
    path = path.split(path.realpath(argv[0]))[0]

    main_part(path)
