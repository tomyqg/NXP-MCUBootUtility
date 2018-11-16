#! /usr/bin/env python
import wx
import sys
import os
import uidef
import uivar
sys.path.append(os.path.abspath(".."))
from win import advSettingsWin_FixedOtpmkKey
from gen import gendef
from run import rundef

class secBootUiSettingsFixedOtpmkKey(advSettingsWin_FixedOtpmkKey.advSettingsWin_FixedOtpmkKey):

    def __init__(self, parent):
        advSettingsWin_FixedOtpmkKey.advSettingsWin_FixedOtpmkKey.__init__(self, parent)
        otpmkKeyOpt, otpmkEncryptedRegionStart, otpmkEncryptedRegionLength = uivar.getAdvancedSettings(uidef.kAdvancedSettings_OtpmkKey)
        self.otpmkKeyOpt = otpmkKeyOpt
        self.otpmkEncryptedRegionStart = otpmkEncryptedRegionStart
        self.otpmkEncryptedRegionLength = otpmkEncryptedRegionLength
        self._recoverLastSettings()

    def _updateRegionInfoField ( self, regionCnt ):
        if regionCnt < 1:
            self.m_textCtrl_region0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            self.m_textCtrl_region0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        else:
            self.m_textCtrl_region0Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_textCtrl_region0Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        if regionCnt < 2:
            self.m_textCtrl_region1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
            self.m_textCtrl_region1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        else:
            self.m_textCtrl_region1Start.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_textCtrl_region1Length.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.Refresh()

    def _recoverLastSettings ( self ):
        keySource = (self.otpmkKeyOpt & 0x0F000000) >> 24
        self.m_choice_keySource.SetSelection(keySource)

        aesMode = (self.otpmkKeyOpt & 0x00F00000) >> 20
        self.m_choice_aesMode.SetSelection(aesMode)

        encryptedRegionCnt = (self.otpmkKeyOpt & 0x000F0000) >> 16
        self.m_choice_regionCnt.SetSelection(encryptedRegionCnt)

        self._updateRegionInfoField(encryptedRegionCnt)

        if encryptedRegionCnt > 0:
            self.m_textCtrl_region0Start.Clear()
            self.m_textCtrl_region0Length.Clear()
            self.m_textCtrl_region0Start.write(str(hex(self.otpmkEncryptedRegionStart[0])))
            self.m_textCtrl_region0Length.write(str(hex(self.otpmkEncryptedRegionLength[0])))
        if encryptedRegionCnt > 1:
            self.m_textCtrl_region1Start.Clear()
            self.m_textCtrl_region1Length.Clear()
            self.m_textCtrl_region1Start.write(str(hex(self.otpmkEncryptedRegionStart[1])))
            self.m_textCtrl_region1Length.write(str(hex(self.otpmkEncryptedRegionLength[1])))

    def _getKeySource( self ):
        txt = self.m_choice_keySource.GetString(self.m_choice_keySource.GetSelection())
        if txt == 'Fuse OTPMK - SNVS':
            val = 0x0
        else:
            pass
        self.otpmkKeyOpt = (self.otpmkKeyOpt & 0xF0FFFFFF) | (val << 24)

    def _getAesMode( self ):
        txt = self.m_choice_aesMode.GetString(self.m_choice_aesMode.GetSelection())
        if txt == 'ECB':
            val = 0x0
        elif txt == 'CTR':
            val = 0x1
        else:
            pass
        self.otpmkKeyOpt = (self.otpmkKeyOpt & 0xFF0FFFFF) | (val << 20)

    def _getEncryptedRegionCount( self ):
        txt = self.m_choice_regionCnt.GetString(self.m_choice_regionCnt.GetSelection())
        val = int(txt[0])
        self.otpmkKeyOpt = (self.otpmkKeyOpt & 0xFFF0FFFF) | (val << 16)

    def popupMsgBox( self, msgStr ):
        messageText = (msgStr)
        wx.MessageBox(messageText, "Error", wx.OK | wx.ICON_INFORMATION)

    def _convertRegionInfoToVal32( self, regionInfoStr ):
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

    def _getEncryptedRegionInfo( self ):
        convertStatus = False
        txt = self.m_choice_regionCnt.GetString(self.m_choice_regionCnt.GetSelection())
        regionCnt = int(txt[0])
        if regionCnt > 0:
            convertStatus, self.otpmkEncryptedRegionStart[0] = self._convertRegionInfoToVal32(self.m_textCtrl_region0Start.GetLineText(0))
            if convertStatus:
                if self.otpmkEncryptedRegionStart[0] < rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR:
                    self.popupMsgBox('FAC Region 0 start address shouldn\'t less than 0x%x' %(rundef.kBootDeviceMemBase_FlexspiNor + gendef.kIvtOffset_NOR))
                    return False
            else:
                return False
            convertStatus, self.otpmkEncryptedRegionLength[0] = self._convertRegionInfoToVal32(self.m_textCtrl_region0Length.GetLineText(0))
            if convertStatus:
                if self.otpmkEncryptedRegionLength[0] % gendef.kSecFacRegionAlignedUnit != 0:
                    self.popupMsgBox('FAC Region 0 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                    return False
            else:
                return False
        else:
            self.otpmkEncryptedRegionStart[0] = None
            self.otpmkEncryptedRegionLength[0] = None
        if regionCnt > 1:
            convertStatus, self.otpmkEncryptedRegionStart[1] = self._convertRegionInfoToVal32(self.m_textCtrl_region1Start.GetLineText(0))
            if convertStatus:
                if self.otpmkEncryptedRegionStart[1] < self.otpmkEncryptedRegionStart[0] + self.otpmkEncryptedRegionLength[0]:
                    self.popupMsgBox('FAC Region 1 start address shouldn\'t less than FAC region 0 end address 0x%x' %(self.otpmkEncryptedRegionStart[0] + self.otpmkEncryptedRegionLength[0]))
                    return False
            else:
                return False
            convertStatus, self.otpmkEncryptedRegionLength[1] = self._convertRegionInfoToVal32(self.m_textCtrl_region1Length.GetLineText(0))
            if convertStatus:
                if self.otpmkEncryptedRegionLength[1] % gendef.kSecFacRegionAlignedUnit != 0:
                    self.popupMsgBox('FAC Region 1 length should be aligned with %dKB' %(gendef.kSecFacRegionAlignedUnit / 0x400))
                    return False
            else:
                return False
        else:
            self.otpmkEncryptedRegionStart[1] = None
            self.otpmkEncryptedRegionLength[1] = None
        return True

    def callbackChangeRegionCount( self, event ):
        txt = self.m_choice_regionCnt.GetString(self.m_choice_regionCnt.GetSelection())
        regionCnt = int(txt[0])
        self._updateRegionInfoField(regionCnt)

    def callbackOk( self, event ):
        self._getKeySource()
        self._getAesMode()
        self._getEncryptedRegionCount()
        if not self._getEncryptedRegionInfo():
            return
        uivar.setAdvancedSettings(uidef.kAdvancedSettings_OtpmkKey, self.otpmkKeyOpt, self.otpmkEncryptedRegionStart, self.otpmkEncryptedRegionLength)
        self.Show(False)

    def callbackCancel( self, event ):
        self.Show(False)
