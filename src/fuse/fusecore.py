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

        self.needToScanFuse = None
        self.scannedFuseList = [None] * fusedef.kMaxEfuseWords
        self.toBeBurnnedFuseList = [None] * fusedef.kMaxEfuseWords
        self.runModeFuseFlagList = [None] * fusedef.kMaxEfuseWords
        self.toBeRefreshedFuseList = [False] * fusedef.kMaxEfuseWords
        self.isRunModeFuseFlagRemapped = False

        self.applyFuseOperToRunMode()

    def _initEntryModeFuseFlag( self ):
        if self.isToolRunAsEntryMode:
            for i in range(fusedef.kMaxEfuseWords):
                if (i >= fusedef.kEfuseEntryModeRegion0IndexStart and i <= fusedef.kEfuseEntryModeRegion0IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion1IndexStart and i <= fusedef.kEfuseEntryModeRegion1IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion2IndexStart and i <= fusedef.kEfuseEntryModeRegion2IndexEnd) or \
                   (i >= fusedef.kEfuseEntryModeRegion3IndexStart and i <= fusedef.kEfuseEntryModeRegion3IndexEnd):
                    self.runModeFuseFlagList[i] = True
                else:
                    self.runModeFuseFlagList[i] = False
        else:
            for i in range(fusedef.kMaxEfuseWords):
                self.runModeFuseFlagList[i] = True

    def applyFuseOperToRunMode( self ):
        self._initEntryModeFuseFlag()
        self.updateFuseRegionField()
        self.isRunModeFuseFlagRemapped = False
        self.needToScanFuse = True

    def _remapRunModeFuseFlagList( self ):
        if self.isRunModeFuseFlagRemapped:
            return
        if self.tgt.hasRemappedFuse:
            for i in range(fusedef.kEfuseRemapLen):
                self.runModeFuseFlagList[fusedef.kEfuseRemapIndex_Src + i], self.runModeFuseFlagList[fusedef.kEfuseRemapIndex_Dest + i] = \
                self.runModeFuseFlagList[fusedef.kEfuseRemapIndex_Dest + i], self.runModeFuseFlagList[fusedef.kEfuseRemapIndex_Src + i]
            self.isRunModeFuseFlagRemapped = True
        else:
            pass

    def _swapRemappedScannedFuseIfAppliable( self ):
        if self.tgt.hasRemappedFuse:
            for i in range(fusedef.kEfuseRemapLen):
                self.scannedFuseList[fusedef.kEfuseRemapIndex_Src + i], self.scannedFuseList[fusedef.kEfuseRemapIndex_Dest + i] = \
                self.scannedFuseList[fusedef.kEfuseRemapIndex_Dest + i], self.scannedFuseList[fusedef.kEfuseRemapIndex_Src + i]
        else:
            pass

    def scanAllFuseRegions( self, needSwapAndShow=True, isRefreshOpt=False ):
        self.needToScanFuse = False
        hasRefreshFuse = False
        self._remapRunModeFuseFlagList()
        for i in range(fusedef.kMaxEfuseWords):
            if self.runModeFuseFlagList[i]:
                if not isRefreshOpt:
                    self.scannedFuseList[i] = self.readMcuDeviceFuseByBlhost(fusedef.kEfuseIndex_START + i, '', False)
                elif self.toBeRefreshedFuseList[i]:
                    self.scannedFuseList[i] = self.readMcuDeviceFuseByBlhost(fusedef.kEfuseIndex_START + i, '', False)
                    self.toBeRefreshedFuseList[i] = False
                    hasRefreshFuse = True
            else:
                self.scannedFuseList[i] = None
        if isRefreshOpt and (not hasRefreshFuse):
            return
        if needSwapAndShow:
            self._swapRemappedScannedFuseIfAppliable()
            self.showScannedFuses(self.scannedFuseList)

    def _swapRemappedToBeBurnFuseIfAppliable( self ):
        if self.tgt.hasRemappedFuse:
            for i in range(fusedef.kEfuseRemapLen):
                self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Src + i], self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Dest + i] = \
                self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Dest + i], self.toBeBurnnedFuseList[fusedef.kEfuseRemapIndex_Src + i]
        else:
            pass

    def burnAllFuseRegions( self ):
        self.toBeBurnnedFuseList = self.getUserFuses()
        self._swapRemappedToBeBurnFuseIfAppliable()
        self._remapRunModeFuseFlagList()
        if self.needToScanFuse:
            self.scanAllFuseRegions(False)
        else:
            self._swapRemappedScannedFuseIfAppliable()
        for i in range(fusedef.kMaxEfuseWords):
            if self.runModeFuseFlagList[i]:
                if self.toBeBurnnedFuseList[i] != self.scannedFuseList[i] and \
                   self.toBeBurnnedFuseList[i] != None and \
                   self.scannedFuseList[i] != None:
                    fuseValue = self.toBeBurnnedFuseList[i] | self.scannedFuseList[i]
                    self.burnMcuDeviceFuseByBlhost(fusedef.kEfuseIndex_START + i, fuseValue)
                    self.toBeRefreshedFuseList[i] = True
        self.scanAllFuseRegions(True, True)
