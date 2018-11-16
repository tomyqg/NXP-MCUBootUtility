#! /usr/bin/env python
import wx
import sys
import os
import uidef
import uivar
sys.path.append(os.path.abspath(".."))
from win import advSettingsWin_FlexibleUserKeys
from gen import gendef
from run import rundef

class secBootUiSettingsFlexibleUserKeys(advSettingsWin_FlexibleUserKeys.advSettingsWin_FlexibleUserKeys):

    def __init__(self, parent):
        advSettingsWin_FlexibleUserKeys.advSettingsWin_FlexibleUserKeys.__init__(self, parent)
        userKeyCtrlDict, userKeyCmdDict = uivar.getAdvancedSettings(uidef.kAdvancedSettings_UserKeys)
        self.userKeyCtrlDict = userKeyCtrlDict
        self.userKeyCmdDict = userKeyCmdDict
        #self._recoverLastSettings()
        self.region0FacStart = [None] * uidef.kMaxFacRegionCount
        self.region0FacLength = [None] * uidef.kMaxFacRegionCount
        self.region1FacStart = [None] * uidef.kMaxFacRegionCount
        self.region1FacLength = [None] * uidef.kMaxFacRegionCount

    def _getDek128ContentFromBinFile( self, filename ):
        if os.path.isfile(filename):
            dek128Content = ''
            with open(filename, 'rb') as fileObj:
                var8Value = fileObj.read(16)
                for i in range(16):
                    temp = str(hex(ord(var8Value[15 - i]) & 0xFF))
                    if len(temp) >= 4 and temp[0:2] == '0x':
                        dek128Content += temp[2:4]
                    else:
                        return None
                fileObj.close()
            return dek128Content
        else:
            return None

    def setNecessaryInfo( self, mcuDevice, otpmkFilename ):
        self.mcuDevice = mcuDevice
        self.otpmkDekContent = self._getDek128ContentFromBinFile(otpmkFilename)
        keySource = None
        if self.mcuDevice == uidef.kMcuDevice_iMXRT102x:
            keySource = uidef.kSupportedKeySource_iMXRT102x
        elif self.mcuDevice == uidef.kMcuDevice_iMXRT105x:
            keySource = uidef.kSupportedKeySource_iMXRT105x
        elif self.mcuDevice == uidef.kMcuDevice_iMXRT106x:
            keySource = uidef.kSupportedKeySource_iMXRT106x
        else:
            pass
        self.m_choice_region0keySource.Clear()
        self.m_choice_region1keySource.Clear()
        self.m_choice_region0keySource.SetItems(keySource)
        self.m_choice_region1keySource.SetItems(keySource)
        self.m_choice_region0keySource.SetSelection(1)
        self.m_choice_region1keySource.SetSelection(1)

    def _getRegionSelection( self ):
        self.userKeyCtrlDict['region_sel'] = self.m_choice_regionSel.GetString(self.m_choice_regionSel.GetSelection())

    def _getBeeEngKeySelection( self ):
        self.userKeyCmdDict['use_zero_key'] = str(self.m_choice_beeEngKeySel.GetSelection())

    def _getImageType( self ):
        self.userKeyCmdDict['is_boot_image'] = str(self.m_choice_imageType.GetSelection())

    def _getXipBaseAddr( self ):
        self.userKeyCmdDict['base_addr'] = self.m_choice_xipBaseAddr.GetString(self.m_choice_xipBaseAddr.GetSelection())

    def _getKeySource( self, regionIndex=0 ):
        if regionIndex == 0:
            self.userKeyCtrlDict['region0_key_src'] = self.m_choice_region0keySource.GetString(self.m_choice_region0keySource.GetSelection())
        elif regionIndex == 1:
            self.userKeyCtrlDict['region1_key_src'] = self.m_choice_region1keySource.GetString(self.m_choice_region1keySource.GetSelection())
        else:
            pass

    def _validateKeyData( self, regionIndex, keyDat ):
        status = False
        if len(keyDat) == 32:
            try:
                val32 = int(keyDat, 16)
                status = True
            except:
                pass
        if not status:
            self.popupMsgBox('Illegal input detected! Region %d Key data should be exactly 128bits (32 chars)' %(regionIndex))
        return status, keyDat

    def _getUserKeyData( self, regionIndex=0 ):
        validateStatus = False
        if regionIndex == 0:
            validateStatus, self.userKeyCmdDict['region0_key'] = self._validateKeyData(regionIndex, self.m_textCtrl_region0UserKeyData.GetLineText(0))
        elif regionIndex == 1:
            if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
                if self.userKeyCtrlDict['region1_key_src'] == self.userKeyCtrlDict['region0_key_src']:
                    validateStatus, self.userKeyCmdDict['region1_key'] = self._validateKeyData(regionIndex, self.m_textCtrl_region0UserKeyData.GetLineText(0))
                else:
                    validateStatus, self.userKeyCmdDict['region1_key'] = self._validateKeyData(regionIndex, self.m_textCtrl_region1UserKeyData.GetLineText(0))
            else:
                validateStatus, self.userKeyCmdDict['region1_key'] = self._validateKeyData(regionIndex, self.m_textCtrl_region1UserKeyData.GetLineText(0))
        else:
            pass
        return validateStatus

    def _getAesMode( self, regionIndex=0 ):
        if regionIndex == 0:
            self.userKeyCmdDict['region0_arg'] = str(self.m_choice_region0AesMode.GetSelection())
        elif regionIndex == 1:
            self.userKeyCmdDict['region1_arg'] = str(self.m_choice_region1AesMode.GetSelection())
        else:
            pass

    def _getFacCount( self, regionIndex=0 ):
        if regionIndex == 0:
            self.userKeyCtrlDict['region0_fac_cnt'] = self.m_choice_region0FacCnt.GetSelection() + 1
        elif regionIndex == 1:
            self.userKeyCtrlDict['region1_fac_cnt'] = self.m_choice_region1FacCnt.GetSelection() + 1
        else:
            pass

    def _getAccessPermision( self, regionIndex=0 ):
        if regionIndex == 0:
            self.userKeyCmdDict['region0_arg'] += str(self.m_choice_region0AccessPermision.GetSelection()) + ']'
        elif regionIndex == 1:
            self.userKeyCmdDict['region1_arg'] += str(self.m_choice_region1AccessPermision.GetSelection()) + ']'
        else:
            pass

    def _validateRegionRange( self, regionInfoStr ):
        status = False
        val32 = None
        if len(regionInfoStr) > 2 and regionInfoStr[0:2] == '0x':
            try:
                val32 = int(regionInfoStr[2:len(regionInfoStr)], 16)
                status = True
            except:
                pass
        if not status:
            self.popupMsgBox('Illegal input detected! You should input like this format: 0x5000')
        return status, val32

    def _getRegionRange( self, regionIndex=0, facIndex=0 ):
        if regionIndex == 0:
            if facIndex == 0:
                validateStatus, self.region0FacStart[0] = self._validateRegionRange(self.m_textCtrl_region0Fac0Start.GetLineText(0))
                if validateStatus:
                    if self.region0FacStart[0] < rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR:
                        self.popupMsgBox('Region 0 FAC 0 start address shouldn\'t less than 0x%x' %(rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR))
                        return False
                else:
                    return False
                validateStatus, self.region0FacLength[0] = self._validateRegionRange(self.m_textCtrl_region0Fac0Length.GetLineText(0))
                if validateStatus:
                    if self.region0FacLength[0] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 0 FAC 0 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region0_arg'] += ',[' + self.m_textCtrl_region0Fac0Start.GetLineText(0) + ',' + self.m_textCtrl_region0Fac0Length.GetLineText(0) + ','
            elif facIndex == 1:
                validateStatus, self.region0FacStart[1] = self._validateRegionRange(self.m_textCtrl_region0Fac1Start.GetLineText(0))
                if validateStatus:
                    if self.region0FacStart[1] < self.region0FacStart[0] + self.region0FacLength[0]:
                        self.popupMsgBox('Region 0 FAC 1 start address shouldn\'t less than Region 0 FAC 0 end address 0x%x' %(self.region0FacStart[0] + self.region0FacLength[0]))
                        return False
                else:
                    return False
                validateStatus, self.region0FacLength[1] = self._validateRegionRange(self.m_textCtrl_region0Fac1Length.GetLineText(0))
                if validateStatus:
                    if self.region0FacLength[1] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 0 FAC 1 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region0_arg'] += ',[' + self.m_textCtrl_region0Fac1Start.GetLineText(0) + ',' + self.m_textCtrl_region0Fac1Length.GetLineText(0) + ','
            elif facIndex == 2:
                validateStatus, self.region0FacStart[2] = self._validateRegionRange(self.m_textCtrl_region0Fac2Start.GetLineText(0))
                if validateStatus:
                    if self.region0FacStart[2] < self.region0FacStart[1] + self.region0FacLength[1]:
                        self.popupMsgBox('Region 0 FAC 2 start address shouldn\'t less than Region 0 FAC 1 end address 0x%x' %(self.region0FacStart[1] + self.region0FacLength[1]))
                        return False
                else:
                    return False
                validateStatus, self.region0FacLength[2] = self._validateRegionRange(self.m_textCtrl_region0Fac2Length.GetLineText(0))
                if validateStatus:
                    if self.region0FacLength[2] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 0 FAC 2 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region0_arg'] += ',[' + self.m_textCtrl_region0Fac2Start.GetLineText(0) + ',' + self.m_textCtrl_region0Fac2Length.GetLineText(0) + ','
            else:
                pass
        elif regionIndex == 1:
            if facIndex == 0:
                validateStatus, self.region1FacStart[0] = self._validateRegionRange(self.m_textCtrl_region1Fac0Start.GetLineText(0))
                if validateStatus:
                    if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
                        if self.region0FacStart[2] != None:
                            if self.region1FacStart[0] < self.region0FacStart[2] + self.region0FacLength[2]:
                                self.popupMsgBox('Region 1 FAC 0 start address shouldn\'t less than Region 0 FAC 2 end address 0x%x' %(self.region0FacStart[2] + self.region0FacLength[2]))
                                return False
                        elif self.region0FacStart[1] != None:
                            if self.region1FacStart[0] < self.region0FacStart[1] + self.region0FacLength[1]:
                                self.popupMsgBox('Region 1 FAC 0 start address shouldn\'t less than Region 0 FAC 1 end address 0x%x' %(self.region0FacStart[1] + self.region0FacLength[1]))
                                return False
                        elif self.region0FacStart[0] != None:
                            if self.region1FacStart[0] < self.region0FacStart[0] + self.region0FacLength[0]:
                                self.popupMsgBox('Region 1 FAC 0 start address shouldn\'t less than Region 0 FAC 0 end address 0x%x' %(self.region0FacStart[0] + self.region0FacLength[0]))
                                return False
                        else:
                            pass
                        # startRegion = self.region0FacStart[2] + self.region0FacLength[2]
                    else:
                        if self.region1FacStart[0] < rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR:
                            self.popupMsgBox('Region 1 FAC 0 start address shouldn\'t less than 0x%x' %(rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR))
                            return False
                else:
                    return False
                validateStatus, self.region1FacLength[0] = self._validateRegionRange(self.m_textCtrl_region1Fac0Length.GetLineText(0))
                if validateStatus:
                    if self.region1FacLength[0] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 1 FAC 0 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region1_arg'] += ',[' + self.m_textCtrl_region1Fac0Start.GetLineText(0) + ',' + self.m_textCtrl_region1Fac0Length.GetLineText(0) + ','
            elif facIndex == 1:
                validateStatus, self.region1FacStart[1] = self._validateRegionRange(self.m_textCtrl_region1Fac1Start.GetLineText(0))
                if validateStatus:
                    if self.region1FacStart[1] < self.region1FacStart[0] + self.region1FacLength[0]:
                        self.popupMsgBox('Region 1 FAC 1 start address shouldn\'t less than Region 1 FAC 0 end address 0x%x' %(self.region1FacStart[0] + self.region1FacLength[0]))
                        return False
                else:
                    return False
                validateStatus, self.region1FacLength[1] = self._validateRegionRange(self.m_textCtrl_region1Fac1Length.GetLineText(0))
                if validateStatus:
                    if self.region1FacLength[1] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 1 FAC 1 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region1_arg'] += ',[' + self.m_textCtrl_region1Fac1Start.GetLineText(0) + ',' + self.m_textCtrl_region1Fac1Length.GetLineText(0) + ','
            elif facIndex == 2:
                validateStatus, self.region1FacStart[2] = self._validateRegionRange(self.m_textCtrl_region1Fac2Start.GetLineText(0))
                if validateStatus:
                    if self.region1FacStart[2] < self.region1FacStart[1] + self.region1FacLength[1]:
                        self.popupMsgBox('Region 1 FAC 2 start address shouldn\'t less than Region 1 FAC 1 end address 0x%x' %(self.region1FacStart[1] + self.region1FacLength[1]))
                        return False
                else:
                    return False
                validateStatus, self.region1FacLength[2] = self._validateRegionRange(self.m_textCtrl_region1Fac2Length.GetLineText(0))
                if validateStatus:
                    if self.region1FacLength[2] % gendef.kSecFacRegionAlignedUnit != 0:
                        self.popupMsgBox('Region 1 FAC 2 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                        return False
                else:
                    return False
                self.userKeyCmdDict['region1_arg'] += ',[' + self.m_textCtrl_region1Fac2Start.GetLineText(0) + ',' + self.m_textCtrl_region1Fac2Length.GetLineText(0) + ','
            else:
                pass
        else:
            pass
        return True

    def _getRegionLock( self, regionIndex=0 ):
        if regionIndex == 0:
            self.userKeyCmdDict['region0_lock'] = str(self.m_choice_region0Lock.GetSelection())
        elif regionIndex == 1:
            self.userKeyCmdDict['region1_lock'] = str(self.m_choice_region1Lock.GetSelection())
        else:
            pass

    def _getRegionArg( self, regionIndex=0 ):
        self._getFacCount(regionIndex)
        self._getAesMode(regionIndex)
        facCnt = 0
        if regionIndex == 0:
            facCnt = self.userKeyCtrlDict['region0_fac_cnt']
        elif regionIndex == 1:
            facCnt = self.userKeyCtrlDict['region1_fac_cnt']
        else:
            pass
        for i in range(facCnt):
            status = self._getRegionRange(regionIndex, i)
            if not status:
                self.region0FacStart = [None] * uidef.kMaxFacRegionCount
                self.region0FacLength = [None] * uidef.kMaxFacRegionCount
                self.region1FacStart = [None] * uidef.kMaxFacRegionCount
                self.region1FacLength = [None] * uidef.kMaxFacRegionCount
                return False
            self._getAccessPermision(regionIndex)

    def _getRegionInfo( self, regionIndex=0 ):
        self._getKeySource(regionIndex)
        if not self._getUserKeyData(regionIndex):
            return False
        if not self._getRegionArg(regionIndex):
            return False
        self._getRegionLock(regionIndex)
        return True

    def _updateKeySourceInfoField ( self, regionIndex=0 ):
        if regionIndex == 0:
            if self.userKeyCtrlDict['region0_key_src'] == uidef.kUserKeySource_OTPMK:
                self.m_textCtrl_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0UserKeyData.Clear()
                if self.otpmkDekContent != None:
                    self.m_textCtrl_region0UserKeyData.write(self.otpmkDekContent)
            else:
                self.m_textCtrl_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
                if self.userKeyCtrlDict['region1_key_src'] == self.userKeyCtrlDict['region0_key_src']:
                    self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                    self.m_textCtrl_region1UserKeyData.Clear()
                else:
                    self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        elif regionIndex == 1:
            if self.userKeyCtrlDict['region1_key_src'] == uidef.kUserKeySource_OTPMK:
                self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1UserKeyData.Clear()
                if self.otpmkDekContent != None:
                    self.m_textCtrl_region1UserKeyData.write(self.otpmkDekContent)
            else:
                if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
                    if self.userKeyCtrlDict['region1_key_src'] == self.userKeyCtrlDict['region0_key_src']:
                        self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                        self.m_textCtrl_region1UserKeyData.Clear()
                    else:
                        self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                else:
                    self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        else:
            pass
        self.Refresh()

    def _updateRegionRangeInfoField ( self, regionIndex=0 ):
        if regionIndex == 0:
            if self.userKeyCtrlDict['region0_fac_cnt'] < 1:
                self.m_staticText_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            if self.userKeyCtrlDict['region0_fac_cnt'] < 2:
                self.m_staticText_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            if self.userKeyCtrlDict['region0_fac_cnt'] < 3:
                self.m_staticText_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        elif regionIndex == 1:
            if self.userKeyCtrlDict['region1_fac_cnt'] < 1:
                self.m_staticText_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            if self.userKeyCtrlDict['region1_fac_cnt'] < 2:
                self.m_staticText_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            if self.userKeyCtrlDict['region1_fac_cnt'] < 3:
                self.m_staticText_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            else:
                self.m_staticText_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        else:
            pass
        self.Refresh()

    def _updateRegionInfoField ( self, regionIndex=0, isRegionEnabled=False ):
        if regionIndex == 0:
            if isRegionEnabled:
                self.m_staticText_region0keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region0Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

                self.m_choice_region0keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region0AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region0FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region0AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region0Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

                self._getKeySource(0)
                self._updateKeySourceInfoField(0)
                self._getFacCount(0)
                self._updateRegionRangeInfoField(0)
            else:
                self.m_staticText_region0keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region0Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )

                self.m_choice_region0keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region0AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region0FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region0Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region0AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region0Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        elif regionIndex == 1:
            if isRegionEnabled:
                self.m_staticText_region1keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_staticText_region1Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

                self.m_choice_region1keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region1AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region1FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_textCtrl_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region1AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
                self.m_choice_region1Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )

                self._getKeySource(1)
                self._updateKeySourceInfoField(1)
                self._getFacCount(1)
                self._updateRegionRangeInfoField(1)
            else:
                self.m_staticText_region1keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_staticText_region1Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )

                self.m_choice_region1keySource.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1UserKeyData.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region1AesMode.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region1FacCnt.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac2Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_textCtrl_region1Fac2Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region1AccessPermision.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
                self.m_choice_region1Lock.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        else:
            pass
        self.Refresh()

    def callbackChangeRegionSelection( self, event ):
        self._getRegionSelection()
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region0:
            self._updateRegionInfoField(0, True)
            self._updateRegionInfoField(1, False)
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region1:
            self._updateRegionInfoField(0, False)
            self._updateRegionInfoField(1, True)
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            self._updateRegionInfoField(0, True)
            self._updateRegionInfoField(1, True)
        else:
            pass

    def callbackChangeRegion0KeySource( self, event ):
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region0 or \
           self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            self._getKeySource(0)
            self._updateKeySourceInfoField(0)

    def popupMsgBox( self, msgStr ):
        messageText = (msgStr)
        wx.MessageBox(messageText, "Error", wx.OK | wx.ICON_INFORMATION)

    def callbackChangeRegion0FacCnt( self, event ):
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region0:
            self._getFacCount(0)
            self._updateRegionRangeInfoField(0)
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            region0FacCnt = self.m_choice_region0FacCnt.GetSelection() + 1
            if region0FacCnt + self.userKeyCtrlDict['region1_fac_cnt'] > uidef.kMaxFacRegionCount:
                self.m_choice_region0FacCnt.SetSelection(self.userKeyCtrlDict['region0_fac_cnt'] - 1)
                self.popupMsgBox('The sum of FAC Region count of Region0 and Region1 must be no more than ' + str(uidef.kMaxFacRegionCount))
            else:
                self._getFacCount(0)
                self._updateRegionRangeInfoField(0)
        else:
            pass

    def callbackChangeRegion1KeySource( self, event ):
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region1 or \
           self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            self._getKeySource(1)
            self._updateKeySourceInfoField(1)


    def callbackChangeRegion1FacCnt( self, event ):
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region1:
            self._getFacCount(1)
            self._updateRegionRangeInfoField(1)
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            region1FacCnt = self.m_choice_region1FacCnt.GetSelection() + 1
            if region1FacCnt + self.userKeyCtrlDict['region0_fac_cnt'] > uidef.kMaxFacRegionCount:
                self.m_choice_region1FacCnt.SetSelection(self.userKeyCtrlDict['region1_fac_cnt'] - 1)
                self.popupMsgBox('The sum of FAC Region count of Region0 and Region1 must be no more than ' + str(uidef.kMaxFacRegionCount))
            else:
                self._getFacCount(1)
                self._updateRegionRangeInfoField(1)
        else:
            pass

    def callbackOk( self, event ):
        self._getRegionSelection()
        if self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region0:
            if not self._getRegionInfo(0):
                return
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_Region1:
            if not self._getRegionInfo(1):
                return
        elif self.userKeyCtrlDict['region_sel'] == uidef.kUserRegionSel_BothRegions:
            if not self._getRegionInfo(0):
                return
            if not self._getRegionInfo(1):
                return
        else:
            pass
        self._getBeeEngKeySelection()
        self._getImageType()
        self._getXipBaseAddr()
        #print 'base_addr=' + self.userKeyCmdDict['base_addr']
        #print 'region0_key=' + self.userKeyCmdDict['region0_key'] + \
        #      ' region0_arg=' + self.userKeyCmdDict['region0_arg'] + \
        #      ' region0_lock=' + self.userKeyCmdDict['region0_lock']
        #print 'region1_key=' + self.userKeyCmdDict['region1_key'] + \
        #      ' region1_arg=' + self.userKeyCmdDict['region1_arg'] + \
        #      ' region1_lock=' + self.userKeyCmdDict['region1_lock']
        #print 'use_zero_key=' + self.userKeyCmdDict['use_zero_key']
        #print 'is_boot_image=' + self.userKeyCmdDict['is_boot_image']
        uivar.setAdvancedSettings(uidef.kAdvancedSettings_UserKeys, self.userKeyCtrlDict, self.userKeyCmdDict)
        self.Show(False)

    def callbackCancel( self, event ):
        self.Show(False)
