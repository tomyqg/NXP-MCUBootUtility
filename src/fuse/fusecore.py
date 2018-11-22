#! /usr/bin/env python
import wx
import sys
import os
import fusedef
sys.path.append(os.path.abspath(".."))
from run import runcore
from ui import uidef

class secBootFuse(runcore.secBootRun):

    def __init__(self, parent):
        runcore.secBootRun.__init__(self, parent)

        self.scannedFuseList = [None] * fusedef.kMaxEfuseWords
        self.toBeBurnnedFuseList = [None] * fusedef.kMaxEfuseWords
        self.entryModeFuseFlagList = [None] * fusedef.kMaxEfuseWords

        self.applyFuseOperToRunMode()

    def _initEntryModeFuseFlag( self ):
        if self.isToolRunAsEntryMode:
            for i in range(fusedef.kMaxEfuseWords):
                if (i >= fusedef.kEfuseEntryModeRegion0IndexStart and i <= fusedef.kEfuseEntryModeRegion0IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion1IndexStart and i <= fusedef.kEfuseEntryModeRegion1IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion2IndexStart and i <= fusedef.kEfuseEntryModeRegion2IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion3IndexStart and i <= fusedef.kEfuseEntryModeRegion3IndexEnd):
                    self.entryModeFuseFlagList[i] = True
                else:
                    self.entryModeFuseFlagList[i] = False
        else:
            for i in range(fusedef.kEfuseRemapLen):
                self.entryModeFuseFlagList[i] = True

    def applyFuseOperToRunMode( self ):
        self._initEntryModeFuseFlag()
        self.updateFuseRegionField()

    def _swapRemappedScannedFuseIfAppliable( self ):
        if self.mcuDevice == uidef.kMcuDevice_iMXRT106x:
            for i in range(fusedef.kEfuseRemapLen):
                self.scannedFuseList[fusedef.kEfuseRemapIndex_Src + i], self.scannedFuseList[fusedef.kEfuseRemapIndex_Dest + i] = \
                self.scannedFuseList[fusedef.kEfuseRemapIndex_Dest + i], self.scannedFuseList[fusedef.kEfuseRemapIndex_Src + i]
        elif self.mcuDevice == uidef.kMcuDevice_iMXRT105x and self.mcuDevice == uidef.kMcuDevice_iMXRT102x:
            pass
        else:
            pass

    def scanAllFuseRegions( self ):
        for i in range(fusedef.kMaxEfuseWords):
            if self.entryModeFuseFlagList[i]:
                self.scannedFuseList[i] = self.readMcuDeviceFuseByBlhost(fusedef.kEfuseIndex_START + i, '', False)
        self._swapRemappedScannedFuseIfAppliable()
        self.showScannedFuses(self.scannedFuseList)

    def _swapRemappedToBeBurnFuseIfAppliable( self ):
        if self.mcuDevice == uidef.kMcuDevice_iMXRT106x:
            for i in range(fusedef.kEfuseRemapLen):
                self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Src + i], self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Dest + i] = \
                self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Dest + i], self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Src + i]
        elif self.mcuDevice == uidef.kMcuDevice_iMXRT105x and self.mcuDevice == uidef.kMcuDevice_iMXRT102x:
            pass
        else:
            pass

    def burnAllFuseRegions( self ):
        self.toBeBurnnedFuseList = self.getUserFuses()
        self._swapRemappedToBeBurnFuseIfAppliable()
        for i in range(fusedef.kMaxEfuseWords):
            if self.entryModeFuseFlagList[i]:
                if self.toBeBurnnedFuseList[i] != self.scannedFuseList[i] and \
                   self.toBeBurnnedFuseList[i] != None and \
                   self.scannedFuseList[i] != None:
                    fuseValue = self.toBeBurnnedFuseList[i] | self.scannedFuseList[i]
                    self.burnMcuDeviceFuseByBlhost(fusedef.kEfuseIndex_START + i, fuseValue)
        self.scanAllFuseRegions()
