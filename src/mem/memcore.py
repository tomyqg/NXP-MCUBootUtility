#! /usr/bin/env python
import sys
import os
import boot
import memdef
sys.path.append(os.path.abspath(".."))
from fuse import fusecore
from run import rundef
from ui import uidef
from ui import uivar
from utils import misc

s_visibleAsciiStart = ' '
s_visibleAsciiEnd = '~'

class secBootMem(fusecore.secBootFuse):

    def __init__(self, parent):
        fusecore.secBootFuse.__init__(self, parent)

        self.needToShowCfgIntr = None
        self.needToShowEkib0Intr = None
        self.needToShowEprdb0Intr = None
        self.needToShowEkib1Intr = None
        self.needToShowEprdb1Intr = None
        self.needToShowIvtIntr = None
        self.needToShowBootDataIntr = None
        self.needToShowDcdIntr = None
        self.needToShowImageIntr = None
        self.needToShowCsfIntr = None
        self.needToShowKeyBlobIntr = None
        self._initShowIntr()

    def _initShowIntr( self ):
        self.needToShowCfgIntr = True
        self.needToShowEkib0Intr = True
        self.needToShowEprdb0Intr = True
        self.needToShowEkib1Intr = True
        self.needToShowEprdb1Intr = True
        self.needToShowIvtIntr = True
        self.needToShowBootDataIntr = True
        self.needToShowDcdIntr = True
        self.needToShowImageIntr = True
        self.needToShowCsfIntr = True
        self.needToShowKeyBlobIntr = True

    def _getCsfBlockInfo( self ):
        self.destAppCsfAddress = self.getVal32FromBinFile(self.destAppFilename, self.destAppIvtOffset + memdef.kMemberOffsetInIvt_Csf)

    def _getInfoFromIvt( self ):
        self._getCsfBlockInfo()

    def _getOneLineContentToShow( self, addr, memLeft, fileObj ):
        memContent = ''
        padBytesBefore= addr % 16
        contentToShow = self.getFormattedHexValue(addr - padBytesBefore) + '    '
        if (padBytesBefore + memLeft) > 16:
            memContent = fileObj.read(16 - padBytesBefore)
        else:
            memContent = fileObj.read(memLeft)
        visibleContent = ''
        for i in range(16):
            if i >= padBytesBefore and \
               i < padBytesBefore + len(memContent):
                halfbyteStr = str(hex((ord(memContent[i-padBytesBefore]) & 0xF0)>> 4))
                contentToShow += halfbyteStr[2]
                halfbyteStr = str(hex((ord(memContent[i-padBytesBefore]) & 0x0F)>> 0))
                contentToShow += halfbyteStr[2] + ' '
                if memContent[i-padBytesBefore] >= s_visibleAsciiStart and \
                   memContent[i-padBytesBefore] <= s_visibleAsciiEnd:
                    visibleContent += memContent[i-padBytesBefore]
                else:
                    visibleContent += '.'
            else:
                contentToShow += '-- '
                visibleContent += '-'
        contentToShow += '        ' + visibleContent
        return contentToShow, memContent

    def readProgrammedMemoryAndShow( self ):
        if not os.path.isfile(self.destAppFilename):
            self.popupMsgBox('You should program your image first!')
            return

        self._getInfoFromIvt()

        memLen = 0
        imageLen = os.path.getsize(self.destAppFilename)
        if self.bootDevice == uidef.kBootDevice_SemcNand:
            semcNandOpt, semcNandFcbOpt, imageInfo = uivar.getBootDeviceConfiguration(self.bootDevice)
            memLen += (imageInfo[self.semcNandImageCopies - 1] >> 16) * self.semcNandBlockSize
        elif self.bootDevice == uidef.kBootDevice_FlexspiNor:
            pass
        else:
            pass
        if self.habDekDataOffset != None and (self.habDekDataOffset + memdef.kMemBlockSize_KeyBlob > imageLen):
            memLen += self.habDekDataOffset + memdef.kMemBlockSize_KeyBlob
        else:
            memLen += imageLen

        memFilename = 'bootDeviceMem.dat'
        memFilepath = os.path.join(self.blhostVectorsDir, memFilename)
        status, results, cmdStr = self.blhost.readMemory(self.bootDeviceMemBase, memLen, memFilename, self.bootDeviceMemId)
        self.printLog(cmdStr)
        if status != boot.status.kStatus_Success:
            return False

        self.clearMem()
        memLen = os.path.getsize(memFilepath)
        memLeft = memLen
        addr = self.bootDeviceMemBase
        with open(memFilepath, 'rb') as fileObj:
            while memLeft > 0:
                contentToShow, memContent = self._getOneLineContentToShow(addr, memLeft, fileObj)
                memLeft -= len(memContent)
                addr += len(memContent)
                if not self.isNandDevice:
                    if addr <= self.bootDeviceMemBase + memdef.kMemBlockSize_CFG:
                        if self.needToShowCfgIntr:
                            self.printMem('------------------------------------FDCB----------------------------------------------', uidef.kMemBlockColor_CFG)
                            self.needToShowCfgIntr = False
                        self.printMem(contentToShow, uidef.kMemBlockColor_CFG)
                    elif addr <= self.bootDeviceMemBase + self.destAppIvtOffset:
                        if self.secureBootType == uidef.kSecureBootType_BeeCrypto:
                            ekib0Start = self.bootDeviceMemBase + memdef.kMemBlockOffset_EKIB0
                            eprdb0Start = self.bootDeviceMemBase + memdef.kMemBlockOffset_EPRDB0
                            ekib1Start = self.bootDeviceMemBase + memdef.kMemBlockOffset_EKIB1
                            eprdb1Start = self.bootDeviceMemBase + memdef.kMemBlockOffset_EPRDB1
                            if addr > ekib0Start and addr <= ekib0Start + memdef.kMemBlockSize_EKIB:
                                if self.needToShowEkib0Intr:
                                    self.printMem('-----------------------------------EKIB0----------------------------------------------', uidef.kMemBlockColor_EKIB)
                                    self.needToShowEkib0Intr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_EKIB)
                            elif addr > eprdb0Start and addr <= eprdb0Start + memdef.kMemBlockSize_EPRDB:
                                if self.needToShowEprdb0Intr:
                                    self.printMem('-----------------------------------EPRDB0---------------------------------------------', uidef.kMemBlockColor_EPRDB)
                                    self.needToShowEprdb0Intr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_EPRDB)
                            elif addr > ekib1Start and addr <= ekib1Start + memdef.kMemBlockSize_EKIB:
                                if self.needToShowEkib1Intr:
                                    self.printMem('-----------------------------------EKIB1----------------------------------------------', uidef.kMemBlockColor_EKIB)
                                    self.needToShowEkib1Intr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_EKIB)
                            elif addr > eprdb1Start and addr <= eprdb1Start + memdef.kMemBlockSize_EPRDB:
                                if self.needToShowEprdb1Intr:
                                    self.printMem('-----------------------------------EPRDB1---------------------------------------------', uidef.kMemBlockColor_EPRDB)
                                    self.needToShowEprdb1Intr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_EPRDB)
                            else:
                                self.printMem(contentToShow)
                        else:
                            self.printMem(contentToShow)
                    elif addr <= self.bootDeviceMemBase + self.destAppIvtOffset + memdef.kMemBlockSize_IVT:
                        if self.needToShowIvtIntr:
                            self.printMem('------------------------------------IVT-----------------------------------------------', uidef.kMemBlockColor_IVT)
                            self.needToShowIvtIntr = False
                        self.printMem(contentToShow, uidef.kMemBlockColor_IVT)
                    elif addr <= self.bootDeviceMemBase + self.destAppIvtOffset + memdef.kMemBlockSize_IVT + memdef.kMemBlockSize_BootData:
                        if self.needToShowBootDataIntr:
                            self.printMem('---------------------------------Boot Data--------------------------------------------', uidef.kMemBlockColor_BootData)
                            self.needToShowBootDataIntr = False
                        self.printMem(contentToShow, uidef.kMemBlockColor_BootData)
                    elif addr <= self.bootDeviceMemBase + self.destAppVectorOffset:
                        self.printMem(contentToShow)
                    elif addr <= self.bootDeviceMemBase + self.destAppVectorOffset + self.destAppBinaryBytes:
                        if self.needToShowImageIntr:
                            self.printMem('-----------------------------------Image----------------------------------------------', uidef.kMemBlockColor_Image)
                            self.needToShowImageIntr = False
                        self.printMem(contentToShow, uidef.kMemBlockColor_Image)
                    else:
                        hasShowed = False
                        if self.secureBootType == uidef.kSecureBootType_HabAuth or self.secureBootType == uidef.kSecureBootType_HabCrypto or \
                           (self.secureBootType == uidef.kSecureBootType_BeeCrypto and self.isCertEnabledForBee):
                            csfStart = self.bootDeviceMemBase + (self.destAppCsfAddress - self.destAppVectorAddress) + self.destAppInitialLoadSize
                            if addr > csfStart and addr <= csfStart + memdef.kMemBlockSize_CSF:
                                if self.needToShowCsfIntr:
                                    self.printMem('------------------------------------CSF-----------------------------------------------', uidef.kMemBlockColor_CSF)
                                    self.needToShowCsfIntr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_CSF)
                                hasShowed = True
                        if self.secureBootType == uidef.kSecureBootType_HabCrypto and self.habDekDataOffset != None:
                            keyBlobStart = self.bootDeviceMemBase + (self.destAppVectorOffset - self.destAppInitialLoadSize) + self.habDekDataOffset
                            if addr > keyBlobStart and addr <= keyBlobStart + memdef.kMemBlockSize_KeyBlob:
                                if self.needToShowKeyBlobIntr:
                                    self.printMem('--------------------------------DEK KeyBlob-------------------------------------------', uidef.kMemBlockColor_KeyBlob)
                                    self.needToShowKeyBlobIntr = False
                                self.printMem(contentToShow, uidef.kMemBlockColor_KeyBlob)
                                hasShowed = True
                        if not hasShowed:
                            self.printMem(contentToShow)
                else:
                    self.printMem(contentToShow)
            fileObj.close()
        self._initShowIntr()
        try:
            os.remove(memFilepath)
        except:
            pass

    def _getUserComMemParameters( self, isMemWrite=False ):
        status = False
        memStart = 0
        memLength = 0
        memBinFile = None
        memFlexibleArg = None
        status, memStart = self.getComMemStartAddress()
        if status:
            if isMemWrite:
                memBinFile = self.getComMemBinFile()
                if not os.path.isfile(memBinFile):
                    status = False
                else:
                    memFlexibleArg = memBinFile
            else:
                status, memLength = self.getComMemByteLength()
                if status:
                    memFlexibleArg = memLength
        return status, memStart, memFlexibleArg

    def _convertComMemStart( self, memStart ):
        if memStart < self.bootDeviceMemBase:
            memStart += self.bootDeviceMemBase
        return memStart

    def readBootDeviceMemory( self ):
        status, memStart, memLength = self._getUserComMemParameters(False)
        if status:
            memStart = self._convertComMemStart(memStart)
            alignedMemStart = misc.align_down(memStart, self.comMemReadUnit)
            alignedMemLength = misc.align_up(memLength, self.comMemReadUnit) + self.comMemReadUnit
            if memLength + memStart > alignedMemStart + self.comMemReadUnit:
                alignedMemLength += self.comMemReadUnit
            memFilename = 'comMemRead.dat'
            memFilepath = os.path.join(self.blhostVectorsDir, memFilename)
            status, results, cmdStr = self.blhost.readMemory(alignedMemStart, alignedMemLength, memFilename, self.bootDeviceMemId)
            self.printLog(cmdStr)
            if status == boot.status.kStatus_Success:
                self.clearMem()
                memLeft = memLength
                addr = memStart
                with open(memFilepath, 'rb') as fileObj:
                    fileObj.seek(memStart - alignedMemStart)
                    while memLeft > 0:
                        contentToShow, memContent = self._getOneLineContentToShow(addr, memLeft, fileObj)
                        memLeft -= len(memContent)
                        addr += len(memContent)
                        self.printMem(contentToShow)
            else:
                self.popupMsgBox('Failed to read boot device, error code is %d !' %(status))

    def eraseBootDeviceMemory( self ):
        status, memStart, memLength = self._getUserComMemParameters(False)
        if status:
            memStart = self._convertComMemStart(memStart)
            alignedMemStart = misc.align_down(memStart, self.comMemEraseUnit)
            alignedMemLength = misc.align_up(memLength, self.comMemEraseUnit)
            if memLength + memStart > alignedMemStart + self.comMemEraseUnit:
                alignedMemLength += self.comMemEraseUnit
            status, results, cmdStr = self.blhost.flashEraseRegion(alignedMemStart, alignedMemLength, self.bootDeviceMemId)
            self.printLog(cmdStr)
            if status != boot.status.kStatus_Success:
                self.popupMsgBox('Failed to erase boot device, error code is %d !' %(status))

    def writeBootDeviceMemory( self ):
        status, memStart, memBinFile = self._getUserComMemParameters(True)
        if status:
            memStart = self._convertComMemStart(memStart)
            if memStart % self.comMemWriteUnit:
                self.popupMsgBox('Start Address should be aligned with 0x%x !' %(self.comMemWriteUnit))
                return
            status, results, cmdStr = self.blhost.writeMemory(memStart, memBinFile, self.bootDeviceMemId)
            self.printLog(cmdStr)
            if status != boot.status.kStatus_Success:
                self.popupMsgBox('Failed to write boot device, error code is %d, You may forget to erase boot device first!' %(status))
