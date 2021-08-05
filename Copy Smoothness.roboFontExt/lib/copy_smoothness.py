from vanilla import (
    ColorWell,
    Button,
    HorizontalLine,
    Window,
    CheckBox,
    PopUpButton,
    TextBox,
    Sheet,
    ProgressBar,
)
from defconAppKit.controls.fontList import FontList
from mojo.roboFont import OpenWindow, AllFonts
from AppKit import NSColor
from lib.tools.misc import NSColorToRgba


class CopySmoothness:
    def __init__(self):
        self.doMarkGlyphs = 0
        self.doPrintStatus = 0
        self.sourceFontList = AllFonts()
        self.destinationFontList = AllFonts()
        self.source_font = self.sourceFontList[0]
        self.destination_fonts = None
        self.mark = NSColor.redColor()

        # create a window
        self.w = Window((350, 500), "Copy Smoothness", minSize=(350, 500))
        self.w.sourceTitle = TextBox((15, 20, 200, 20), "Source Font:")
        self.w.sourceFont = PopUpButton(
            (15, 41, -20, 20),
            [f.info.familyName + " " + f.info.styleName for f in self.sourceFontList],
            callback=self.sourceCallback,
        )
        self.w.desTitle = TextBox((15, 80, 200, 20), "Destination Fonts:")
        self.w.destinationFonts = FontList(
            (15, 100, -15, -105),
            self.destinationFontList,
            selectionCallback=self.desCallback,
        )
        self.w.markGlyphs = CheckBox(
            (20, -84, 100, 22),
            "Mark Glyphs",
            callback=self.markCallback,
            value=self.doMarkGlyphs,
        )
        self.w.printStatus = CheckBox(
            (130, -84, 190, 22),
            "Print status to output (slow)",
            callback=self.printStatusCallback,
            value=self.doPrintStatus,
        )
        self.w.copyButton = Button(
            (-140, -40, 120, 20), "Copy Smoothness", callback=self.copyCallback
        )
        self.w.line = HorizontalLine((10, -50, -10, 1))
        self._updateDest()

        # open the window
        self.w.open()

    def _updateDest(self):
        des = list(self.sourceFontList)
        des.remove(self.source_font)
        self.w.destinationFonts.set(des)

    def copyType(self, source_font, destination_fonts, mark):
        for font in destination_fonts:
            if self.doPrintStatus == 1:
                print(f'Copying smoothness to {font.path}')
            for g in source_font:
                if g.name in font.keys():
                    dest = font[g.name]
                    if dest.isCompatible(g):
                        if self.doPrintStatus == 1:
                            print(f'    {g.name}:')
                        changed = False
                        index = 0
                        dest.prepareUndo("Copy smoothness")
                        for c in g:
                            types = []
                            for p in c.points:
                                types.append(p.smooth)
                            i = 0
                            for p in dest[index].points:
                                if p.smooth != types[i] and p.type != "offCurve":
                                    p.smooth = types[i]
                                    changed = True
                                i += 1
                            index += 1
                        if changed:
                            if self.doPrintStatus == 1:
                                print('      Copied smoothness')
                            if mark == 1:
                                dest.mark = NSColorToRgba(self.mark)
                            dest.changed()
                        else:
                            if self.doPrintStatus == 1:
                                print('      Smoothness the same, no copy')
                        dest.performUndo()
                    else:
                        if self.doPrintStatus == 1:
                            print(f'    {g.name}: Not compatiable')

    def markCallback(self, sender):
        self.doMarkGlyphs = sender.get()
        if self.doMarkGlyphs == 1:
            self.w.colorWell = ColorWell(
                (-220, -85, 100, 23), callback=self.colorCallback, color=self.mark
            )
        else:
            del self.w.colorWell

    def colorCallback(self, sender):
        self.mark = sender.get()

    def printStatusCallback(self, sender):
        self.doPrintStatus = sender.get()

    def sourceCallback(self, sender):
        self.source_font = self.sourceFontList[sender.get()]
        self._updateDest()

    def desCallback(self, sender):
        self.destination_fonts = [sender.get()[x] for x in sender.getSelection()]

    def copyCallback(self, sender):
        self.sheet = Sheet((300, 50), self.w)
        self.sheet.bar = ProgressBar(
            (10, 20, -10, 10), isIndeterminate=True, sizeStyle="small"
        )
        self.sheet.open()
        self.sheet.bar.start()
        self.copyType(self.source_font, self.destination_fonts, self.doMarkGlyphs)
        self.sheet.bar.stop()
        self.sheet.close()
        del self.sheet
        self.w.close()


OpenWindow(CopySmoothness)
