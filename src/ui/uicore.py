#! /usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import time
import serial.tools.list_ports
import pywinusb.hid
import threading
import uidef
import uivar
sys.path.append(os.path.abspath(".."))
from win import secBootWin
from run import rundef
from fuse import fusedef

kRetryDetectTimes = 5

s_isGaugeWorking = False
s_curGauge = 0
s_maxGauge = 0

class secBootUi(secBootWin.secBootWin):

    def __init__(self, parent):
        secBootWin.secBootWin.__init__(self, parent)
        self.m_bitmap_nxp.SetBitmap(wx.Bitmap( u"../img/logo_nxp.png", wx.BITMAP_TYPE_ANY ))

        self.exeBinRoot = os.getcwd()
        self.exeTopRoot = os.path.dirname(self.exeBinRoot)
        exeMainFile = os.path.join(self.exeTopRoot, 'src', 'main.py')
        if not os.path.isfile(exeMainFile):
            self.exeTopRoot = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        uivar.initVar(os.path.join(self.exeTopRoot, 'bin', 'nsb_settings.json'))
        toolCommDict = uivar.getAdvancedSettings(uidef.kAdvancedSettings_Tool)
        self.toolCommDict = toolCommDict.copy()

        self.logFolder = os.path.join(self.exeTopRoot, 'gen', 'log_file')
        self.logFilename = os.path.join(self.exeTopRoot, 'gen', 'log_file', 'log.txt')

        self.isToolRunAsEntryMode = None
        self._initToolRunMode()
        self.setToolRunMode()

        self.updateConnectStatus()

        self.mcuSeries = None
        self.mcuDevice = None
        self.bootDevice = None
        self.isNandDevice = False
        self._initTargetSetupValue()
        self.setTargetSetupValue()

        self.isUartPortSelected = None
        self.isUsbhidPortSelected = None
        self.uartComPort = None
        self.uartBaudrate = None
        self.usbhidVid = None
        self.usbhidPid = None
        self.isUsbhidConnected = False
        self.usbhidToConnect = [None] * 2
        self._initPortSetupValue()
        self.usbhidDetectTimer = None
        self.periodicUsbhidDetectTask()
        self.isOneStepConnectMode = None
        self.initOneStepConnectMode()

        self.secureBootType = None
        self.keyStorageRegion = None
        self.isCertEnabledForBee = None
        self._initSecureBootSeqValue()
        self._initSecureBootSeqColor()

    def _initToolRunMode( self ):
        if self.toolCommDict['isToolRunAsEntryMode']:
            self.m_menuItem_entryMode.Check(True)
            self.m_menuItem_masterMode.Check(False)
        else:
            self.m_menuItem_entryMode.Check(False)
            self.m_menuItem_masterMode.Check(True)

    def setToolRunMode( self ):
        self.isToolRunAsEntryMode = self.m_menuItem_entryMode.IsChecked()
        self.toolCommDict['isToolRunAsEntryMode'] = self.isToolRunAsEntryMode

    def _initTargetSetupValue( self ):
        self.m_choice_mcuSeries.Clear()
        self.m_choice_bootDevice.Clear()
        self.m_choice_mcuSeries.SetItems(uidef.kMcuSeries_v0_11_x)
        self.m_choice_bootDevice.SetItems(uidef.kBootDevice_v0_11_x)
        self.m_choice_mcuSeries.SetSelection(self.toolCommDict['mcuSeries'])
        self.m_choice_mcuDevice.SetSelection(self.toolCommDict['mcuDevice'])
        self.m_choice_bootDevice.SetSelection(self.toolCommDict['bootDevice'])

    def setTargetSetupValue( self ):
        self.mcuSeries = self.m_choice_mcuSeries.GetString(self.m_choice_mcuSeries.GetSelection())
        self.mcuDevice = self.m_choice_mcuDevice.GetString(self.m_choice_mcuDevice.GetSelection())
        self.bootDevice = self.m_choice_bootDevice.GetString(self.m_choice_bootDevice.GetSelection())
        self.toolCommDict['mcuSeries'] = self.m_choice_mcuSeries.GetSelection()
        self.toolCommDict['mcuDevice'] = self.m_choice_mcuDevice.GetSelection()
        self.toolCommDict['bootDevice'] = self.m_choice_bootDevice.GetSelection()
        if self.bootDevice == uidef.kBootDevice_FlexspiNor or \
           self.bootDevice == uidef.kBootDevice_SemcNor or \
           self.bootDevice == uidef.kBootDevice_LpspiNor:
            self.isNandDevice = False
        elif self.bootDevice == uidef.kBootDevice_FlexspiNand or \
             self.bootDevice == uidef.kBootDevice_SemcNand or \
             self.bootDevice == uidef.kBootDevice_UsdhcSd or \
             self.bootDevice == uidef.kBootDevice_UsdhcMmc:
            self.isNandDevice = True
        else:
            pass

    def _initPortSetupValue( self ):
        if self.toolCommDict['isUsbhidPortSelected']:
            self.m_radioBtn_uart.SetValue(False)
            self.m_radioBtn_usbhid.SetValue(True)
        else:
            self.m_radioBtn_uart.SetValue(True)
            self.m_radioBtn_usbhid.SetValue(False)
        usbIdList = self.getUsbid()
        self.setPortSetupValue(uidef.kConnectStage_Rom, usbIdList)

    def periodicUsbhidDetectTask( self ):
        if self.isUsbhidPortSelected:
            self._retryToDetectUsbhidDevice(False)
            self.usbhidDetectTimer = threading.Timer(1, self.periodicUsbhidDetectTask)
            self.usbhidDetectTimer.start()

    def _retryToDetectUsbhidDevice( self, needToRetry = True ):
        usbVid = [None]
        usbPid = [None]
        self.isUsbhidConnected = False
        retryCnt = 1
        if needToRetry:
            retryCnt = kRetryDetectTimes
        while retryCnt > 0:
            # Auto detect USB-HID device
            hidFilter = pywinusb.hid.HidDeviceFilter(vendor_id = int(self.usbhidToConnect[0], 16), product_id = int(self.usbhidToConnect[1], 16))
            hidDevice = hidFilter.get_devices()
            if len(hidDevice) > 0:
                self.isUsbhidConnected = True
                usbVid[0] = self.usbhidToConnect[0]
                usbPid[0] = self.usbhidToConnect[1]
                break
            retryCnt = retryCnt - 1
            if retryCnt != 0:
                time.sleep(2)
            else:
                usbVid[0] = 'N/A - Not Found'
                usbPid[0] = usbVid[0]
        if self.m_choice_portVid.GetString(self.m_choice_portVid.GetSelection()) != usbVid[0]:
            self.m_choice_portVid.Clear()
            self.m_choice_baudPid.Clear()
            self.m_choice_portVid.SetItems(usbVid)
            self.m_choice_baudPid.SetItems(usbPid)
            self.m_choice_portVid.SetSelection(0)
            self.m_choice_baudPid.SetSelection(0)

    def adjustPortSetupValue( self, connectStage=uidef.kConnectStage_Rom, usbIdList=[] ):
        self.isUartPortSelected = self.m_radioBtn_uart.GetValue()
        self.isUsbhidPortSelected = self.m_radioBtn_usbhid.GetValue()
        if self.isUartPortSelected:
            self.m_staticText_portVid.SetLabel('COM Port:')
            self.m_staticText_baudPid.SetLabel('Baudrate:')
            # Auto detect available ports
            comports = list(serial.tools.list_ports.comports())
            ports = [None] * len(comports)
            for i in range(len(comports)):
                comport = list(comports[i])
                ports[i] = comport[0]
            lastPort = self.m_choice_portVid.GetString(self.m_choice_portVid.GetSelection())
            lastBaud = self.m_choice_baudPid.GetString(self.m_choice_baudPid.GetSelection())
            self.m_choice_portVid.Clear()
            self.m_choice_baudPid.Clear()
            self.m_choice_portVid.SetItems(ports)
            baudItems = ['115200']
            if connectStage == uidef.kConnectStage_Rom:
                baudItems = rundef.kUartSpeed_Sdphost
            elif connectStage == uidef.kConnectStage_Flashloader:
                baudItems = rundef.kUartSpeed_Blhost
            else:
                pass
            self.m_choice_baudPid.SetItems(baudItems)
            if lastPort in ports:
                self.m_choice_portVid.SetSelection(self.m_choice_portVid.FindString(lastPort))
            else:
                self.m_choice_portVid.SetSelection(0)
            if lastBaud in baudItems:
                self.m_choice_baudPid.SetSelection(self.m_choice_baudPid.FindString(lastBaud))
            else:
                self.m_choice_baudPid.SetSelection(0)
        elif self.isUsbhidPortSelected:
            self.m_staticText_portVid.SetLabel('Vendor ID:')
            self.m_staticText_baudPid.SetLabel('Product ID:')
            if connectStage == uidef.kConnectStage_Rom:
                self.usbhidToConnect[0] = usbIdList[0]
                self.usbhidToConnect[1] = usbIdList[1]
                self._retryToDetectUsbhidDevice(False)
            elif connectStage == uidef.kConnectStage_Flashloader:
                self.usbhidToConnect[0] = usbIdList[2]
                self.usbhidToConnect[1] = usbIdList[3]
                self._retryToDetectUsbhidDevice(False)
            else:
                pass
        else:
            pass

    def setPortSetupValue( self, connectStage=uidef.kConnectStage_Rom, usbIdList=[], retryToDetectUsb=False, showError=False ):
        self.adjustPortSetupValue(connectStage, usbIdList)
        self.updatePortSetupValue(retryToDetectUsb, showError)

    def updatePortSetupValue( self, retryToDetectUsb=False, showError=False ):
        status = True
        self.isUartPortSelected = self.m_radioBtn_uart.GetValue()
        self.isUsbhidPortSelected = self.m_radioBtn_usbhid.GetValue()
        if self.isUartPortSelected:
            self.uartComPort = self.m_choice_portVid.GetString(self.m_choice_portVid.GetSelection())
            self.uartBaudrate = self.m_choice_baudPid.GetString(self.m_choice_baudPid.GetSelection())
        elif self.isUsbhidPortSelected:
            if self.isUsbhidConnected:
                self.usbhidVid = self.m_choice_portVid.GetString(self.m_choice_portVid.GetSelection())
                self.usbhidPid = self.m_choice_baudPid.GetString(self.m_choice_baudPid.GetSelection())
            else:
                self._retryToDetectUsbhidDevice(retryToDetectUsb)
                if not self.isUsbhidConnected:
                    status = False
                    if showError:
                        self.popupMsgBox('Cannnot find USB-HID device (vid=%s, pid=%s), Please connect USB cable to your board first!' %(self.usbhidToConnect[0], self.usbhidToConnect[1]))
                else:
                    self.usbhidVid = self.m_choice_portVid.GetString(self.m_choice_portVid.GetSelection())
                    self.usbhidPid = self.m_choice_baudPid.GetString(self.m_choice_baudPid.GetSelection())
        else:
            pass
        self.toolCommDict['isUsbhidPortSelected'] = self.isUsbhidPortSelected
        return status

    def updateConnectStatus( self, color='black' ):
        if color == 'black':
            self.m_button_connect.SetLabel('Connect to ROM')
            self.m_bitmap_connectLed.SetBitmap(wx.Bitmap( u"../img/led_black.png", wx.BITMAP_TYPE_ANY ))
        elif color == 'yellow':
            self.m_button_connect.SetLabel('Connect to Flashloader')
            self.m_bitmap_connectLed.SetBitmap(wx.Bitmap( u"../img/led_yellow.png", wx.BITMAP_TYPE_ANY ))
        elif color == 'green':
            self.m_button_connect.SetLabel('Configure boot device')
            self.m_bitmap_connectLed.SetBitmap(wx.Bitmap( u"../img/led_green.png", wx.BITMAP_TYPE_ANY ))
        elif color == 'blue':
            self.m_button_connect.SetLabel('Reset device')
            self.m_bitmap_connectLed.SetBitmap(wx.Bitmap( u"../img/led_blue.png", wx.BITMAP_TYPE_ANY ))
        elif color == 'red':
            self.m_button_connect.SetLabel('Reconnect')
            self.m_bitmap_connectLed.SetBitmap(wx.Bitmap( u"../img/led_red.png", wx.BITMAP_TYPE_ANY ))
        else:
            pass

    def initOneStepConnectMode( self ):
        self.m_checkBox_oneStepConnect.SetValue(self.toolCommDict['isOneStepChecked'])
        self.getOneStepConnectMode()

    def getOneStepConnectMode( self ):
        self.isOneStepConnectMode = self.m_checkBox_oneStepConnect.GetValue()
        self.toolCommDict['isOneStepChecked'] = self.isOneStepConnectMode

    def enableOneStepForEntryMode( self ):
        if self.isToolRunAsEntryMode:
            self.m_checkBox_oneStepConnect.SetValue(True)
            self.toolCommDict['isOneStepChecked'] = True

    def _initSecureBootSeqValue( self ):
        self.m_choice_secureBootType.SetSelection(self.toolCommDict['secBootType'])
        self.m_textCtrl_serial.Clear()
        self.m_textCtrl_serial.write(self.toolCommDict['certSerial'])
        self.m_textCtrl_keyPass.Clear()
        self.m_textCtrl_keyPass.write(self.toolCommDict['certKeyPass'])
        if self.toolCommDict['appFilename'] != None:
            self.m_filePicker_appPath.SetPath(self.toolCommDict['appFilename'])
        self.m_choice_appFormat.SetSelection(self.toolCommDict['appFormat'])
        self._setUserBinaryBaseField()
        self.m_textCtrl_appBaseAddr.Clear()
        self.m_textCtrl_appBaseAddr.write(self.toolCommDict['appBinBaseAddr'])
        self.m_choice_keyStorageRegion.SetSelection(self.toolCommDict['keyStoreRegion'])
        self.m_choice_enableCertForBee.SetSelection(self.toolCommDict['certOptForBee'])

    def _initSecureBootSeqColor ( self ):
        self.secureBootType = self.m_choice_secureBootType.GetString(self.m_choice_secureBootType.GetSelection())
        self.keyStorageRegion = self.m_choice_keyStorageRegion.GetString(self.m_choice_keyStorageRegion.GetSelection())
        self.setSecureBootSeqColor()

    def _resetSecureBootSeqColor( self ):
        self._resetCertificateColor()
        self.m_panel_genImage1_browseApp.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_genImage1_browseApp.Enable( False )
        self.m_panel_genImage2_habCryptoAlgo.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_genImage2_habCryptoAlgo.Enable( False )
        self.m_panel_genImage3_enableCertForBee.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_genImage3_enableCertForBee.Enable( False )
        self.m_button_genImage.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_genImage.Enable( False )
        self._resetKeyStorageRegionColor()
        self.m_panel_flashImage1_showImage.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_flashImage1_showImage.Enable( False )
        self.m_button_flashImage.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_flashImage.Enable( False )
        self.m_panel_progDek1_showHabDek.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_progDek1_showHabDek.Enable( False )
        self.m_textCtrl_habDek128bit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_textCtrl_habDek128bit.Enable( False )
        self.m_button_progDek.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_progDek.Enable( False )
        self.Refresh()

    def _resetKeyStorageRegionColor( self ):
        self.m_panel_prepBee1_beeKeyRegion.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_prepBee1_beeKeyRegion.Enable( False )
        self.m_panel_prepBee2_beeCryptoAlgo.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_prepBee2_beeCryptoAlgo.Enable( False )
        self.m_button_prepBee.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_prepBee.Enable( False )
        self.m_panel_operBee1_beeKeyInfo.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_operBee1_beeKeyInfo.Enable( False )
        self.m_panel_operBee2_showGp4Dek.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_operBee2_showGp4Dek.Enable( False )
        self.m_textCtrl_gp4Dek128bit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_textCtrl_gp4Dek128bit.Enable( False )
        self.m_panel_operBee3_showSwgp2Dek.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_operBee3_showSwgp2Dek.Enable( False )
        self.m_textCtrl_swgp2Dek128bit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_textCtrl_swgp2Dek128bit.Enable( False )
        self.m_button_operBee.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_operBee.Enable( False )
        self.Refresh()

    def _resetCertificateColor( self ):
        self.m_panel_doAuth1_certInput.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_textCtrl_serial.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_textCtrl_keyPass.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_panel_doAuth1_certInput.Enable( False )
        self.m_panel_doAuth2_certFmt.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_doAuth2_certFmt.Enable( False )
        self.m_button_genCert.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_genCert.Enable( False )
        self.m_panel_progSrk1_showSrk.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_panel_progSrk1_showSrk.Enable( False )
        self.m_textCtrl_srk256bit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_GRAYTEXT ) )
        self.m_textCtrl_srk256bit.Enable( False )
        self.m_button_progSrk.SetBackgroundColour( uidef.kBootSeqColor_Invalid )
        self.m_button_progSrk.Enable( False )
        self.Refresh()

    def invalidateStepButtonColor( self, stepName, excuteResult ):
        invalidColor = None
        if excuteResult:
            invalidColor = uidef.kBootSeqColor_Invalid
        else:
            invalidColor = uidef.kBootSeqColor_Failed
        if stepName == uidef.kSecureBootSeqStep_AllInOne:
            self.m_button_allInOneAction.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_GenCert:
            self.m_button_genCert.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_GenImage:
            self.m_button_genImage.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_PrepBee:
            self.m_button_prepBee.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_ProgSrk:
            self.m_button_progSrk.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_OperBee:
            self.m_button_operBee.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_FlashImage:
            self.m_button_flashImage.SetBackgroundColour( invalidColor )
        elif stepName == uidef.kSecureBootSeqStep_ProgDek:
            self.m_button_progDek.SetBackgroundColour( invalidColor )
        else:
            pass
        self.Refresh()

    def setSecureBootButtonColor( self ):
        activeColor = None
        optionalColor = None
        setEnable = None
        if self.isToolRunAsEntryMode:
            activeColor = uidef.kBootSeqColor_Invalid
            optionalColor = uidef.kBootSeqColor_Invalid
        else:
            activeColor = uidef.kBootSeqColor_Active
            optionalColor = uidef.kBootSeqColor_Optional
        setEnable = not self.isToolRunAsEntryMode
        self.secureBootType = self.m_choice_secureBootType.GetString(self.m_choice_secureBootType.GetSelection())
        if self.secureBootType == uidef.kSecureBootType_Development:
            self.m_button_genImage.Enable( setEnable )
            self.m_button_genImage.SetBackgroundColour( activeColor )
            self.m_button_flashImage.Enable( setEnable )
            self.m_button_flashImage.SetBackgroundColour( activeColor )
        elif self.secureBootType == uidef.kSecureBootType_HabAuth:
            self.m_button_genCert.Enable( setEnable )
            self.m_button_genCert.SetBackgroundColour( activeColor )
            self.m_button_genImage.Enable( setEnable )
            self.m_button_genImage.SetBackgroundColour( activeColor )
            self.m_button_progSrk.Enable( setEnable )
            self.m_button_progSrk.SetBackgroundColour( activeColor )
            self.m_button_flashImage.Enable( setEnable )
            self.m_button_flashImage.SetBackgroundColour( activeColor )
        elif self.secureBootType == uidef.kSecureBootType_HabCrypto:
            self.m_button_genCert.Enable( setEnable )
            self.m_button_genCert.SetBackgroundColour( activeColor )
            self.m_button_genImage.Enable( setEnable )
            self.m_button_genImage.SetBackgroundColour( activeColor )
            self.m_button_progSrk.Enable( setEnable )
            self.m_button_progSrk.SetBackgroundColour( activeColor )
            self.m_button_flashImage.Enable( setEnable )
            self.m_button_flashImage.SetBackgroundColour( activeColor )
            self.m_button_progDek.Enable( setEnable )
            self.m_button_progDek.SetBackgroundColour( activeColor )
        elif self.secureBootType == uidef.kSecureBootType_BeeCrypto:
            if self.bootDevice == uidef.kBootDevice_FlexspiNor:
                if self.isCertEnabledForBee:
                    self.m_button_genCert.Enable( setEnable )
                    self.m_button_genCert.SetBackgroundColour( optionalColor )
                    self.m_button_progSrk.Enable( setEnable )
                    self.m_button_progSrk.SetBackgroundColour( optionalColor )
                if self.keyStorageRegion == uidef.kKeyStorageRegion_FixedOtpmkKey:
                    self.m_button_prepBee.Enable( setEnable )
                    self.m_button_prepBee.SetBackgroundColour( activeColor )
                elif self.keyStorageRegion == uidef.kKeyStorageRegion_FlexibleUserKeys:
                    self.m_button_prepBee.Enable( setEnable )
                    self.m_button_prepBee.SetBackgroundColour( activeColor )
                    self.m_button_operBee.Enable( setEnable )
                    self.m_button_operBee.SetBackgroundColour( activeColor )
                else:
                    pass
                self.m_button_genImage.Enable( setEnable )
                self.m_button_genImage.SetBackgroundColour( activeColor )
                self.m_button_flashImage.Enable( setEnable )
                self.m_button_flashImage.SetBackgroundColour( activeColor )
        else:
            pass
        self.m_button_allInOneAction.Enable( True )
        self.m_button_allInOneAction.SetBackgroundColour( uidef.kBootSeqColor_Active )
        self.Refresh()

    def _getImgName( self ):
        memType = ''
        hasDcd = ''
        if self.isNandDevice:
            memType = 'nand_'
        else:
            memType = 'nor_'
        dcdCtrlDict, dcdSettingsDict = uivar.getBootDeviceConfiguration(uidef.kBootDevice_Dcd)
        if dcdCtrlDict['isDcdEnabled']:
            hasDcd = 'dcd_'
        return memType, hasDcd

    def setSecureBootSeqColor( self ):
        self.secureBootType = self.m_choice_secureBootType.GetString(self.m_choice_secureBootType.GetSelection())
        self.toolCommDict['secBootType'] = self.m_choice_secureBootType.GetSelection()
        self._resetSecureBootSeqColor()
        if self.secureBootType == uidef.kSecureBootType_Development:
            self.m_panel_genImage1_browseApp.Enable( True )
            self.m_panel_genImage1_browseApp.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_button_genImage.SetLabel('Generate Unsigned Bootable Image')
            self.m_panel_flashImage1_showImage.Enable( True )
            self.m_panel_flashImage1_showImage.SetBackgroundColour( uidef.kBootSeqColor_Active )
            strMemType, strHasDcd = self._getImgName()
            imgPath = "../img/" + strMemType + "image_" + strHasDcd + "unsigned.png"
            self.showImageLayout(imgPath.encode('utf-8'))
            self.m_button_flashImage.SetLabel('Load Unsigned Image')
        elif self.secureBootType == uidef.kSecureBootType_HabAuth:
            self.m_panel_doAuth1_certInput.Enable( True )
            self.m_panel_doAuth1_certInput.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_textCtrl_serial.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_textCtrl_keyPass.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_panel_doAuth2_certFmt.Enable( True )
            self.m_panel_doAuth2_certFmt.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_genImage1_browseApp.Enable( True )
            self.m_panel_genImage1_browseApp.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_button_genImage.SetLabel('Generate Signed Bootable Image')
            self.m_panel_progSrk1_showSrk.Enable( True )
            self.m_panel_progSrk1_showSrk.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_flashImage1_showImage.Enable( True )
            self.m_panel_flashImage1_showImage.SetBackgroundColour( uidef.kBootSeqColor_Active )
            strMemType, strHasDcd = self._getImgName()
            imgPath = "../img/" + strMemType + "image_" + strHasDcd + "signed.png"
            self.showImageLayout(imgPath.encode('utf-8'))
            self.m_button_flashImage.SetLabel('Load Signed Image')
        elif self.secureBootType == uidef.kSecureBootType_HabCrypto:
            self.m_panel_doAuth1_certInput.Enable( True )
            self.m_panel_doAuth1_certInput.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_textCtrl_serial.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_textCtrl_keyPass.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_panel_doAuth2_certFmt.Enable( True )
            self.m_panel_doAuth2_certFmt.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_genImage1_browseApp.Enable( True )
            self.m_panel_genImage1_browseApp.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_genImage2_habCryptoAlgo.Enable( True )
            self.m_panel_genImage2_habCryptoAlgo.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_button_genImage.SetLabel('Generate Encrypted Bootable Image,DEK')
            self.m_panel_progSrk1_showSrk.Enable( True )
            self.m_panel_progSrk1_showSrk.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_flashImage1_showImage.Enable( True )
            self.m_panel_flashImage1_showImage.SetBackgroundColour( uidef.kBootSeqColor_Active )
            strMemType, strHasDcd = self._getImgName()
            imgPath = "../img/" + strMemType + "image_" + strHasDcd + "signed_hab_encrypted_nodek.png"
            self.showImageLayout(imgPath.encode('utf-8'))
            self.m_button_flashImage.SetLabel('Load Encrypted Image')
            self.m_panel_progDek1_showHabDek.Enable( True )
            self.m_panel_progDek1_showHabDek.SetBackgroundColour( uidef.kBootSeqColor_Active )
        elif self.secureBootType == uidef.kSecureBootType_BeeCrypto:
            if self.bootDevice == uidef.kBootDevice_FlexspiNor:
                self.m_panel_genImage1_browseApp.Enable( True )
                self.m_panel_genImage1_browseApp.SetBackgroundColour( uidef.kBootSeqColor_Active )
                self.m_panel_genImage3_enableCertForBee.Enable( True )
                self.m_panel_genImage3_enableCertForBee.SetBackgroundColour( uidef.kBootSeqColor_Active )
                self.setKeyStorageRegionColor()
                self.setBeeCertColor()
                self.m_panel_flashImage1_showImage.Enable( True )
                self.m_panel_flashImage1_showImage.SetBackgroundColour( uidef.kBootSeqColor_Active )
                strMemType, strHasDcd = self._getImgName()
                imgPath = ""
                if self.isCertEnabledForBee:
                    self.m_button_genImage.SetLabel('Generate Signed Bootable Image')
                    imgPath = "../img/nor_image_" + strHasDcd + "signed_bee_encrypted.png"
                else:
                    self.m_button_genImage.SetLabel('Generate Unsigned Bootable Image')
                    imgPath = "../img/nor_image_" + strHasDcd + "unsigned_bee_encrypted.png"
                self.showImageLayout(imgPath.encode('utf-8'))
                self.m_button_flashImage.SetLabel('Load Encrypted Image')
            else:
                self._resetSecureBootSeqColor()
        else:
            pass
        self.setSecureBootButtonColor()
        self.Refresh()

    def updateImgPictureAfterFlashDek( self ):
        strMemType, strHasDcd = self._getImgName()
        imgPath = "../img/" + strMemType + "image_" + strHasDcd + "signed_hab_encrypted.png"
        self.showImageLayout(imgPath.encode('utf-8'))

    def getSerialAndKeypassContent( self ):
        serialContent = self.m_textCtrl_serial.GetLineText(0)
        keypassContent = self.m_textCtrl_keyPass.GetLineText(0)
        self.toolCommDict['certSerial'] = serialContent
        self.toolCommDict['certKeyPass'] = keypassContent
        return serialContent, keypassContent

    def setBeeCertColor( self ):
        txt = self.m_choice_enableCertForBee.GetString(self.m_choice_enableCertForBee.GetSelection())
        self.toolCommDict['certOptForBee'] = self.m_choice_enableCertForBee.GetSelection()
        strMemType, strHasDcd = self._getImgName()
        imgPath = ""
        if txt == 'No':
            self.isCertEnabledForBee = False
            self.m_button_genImage.SetLabel('Generate Unsigned Bootable Image')
            imgPath = "../img/nor_image_" + strHasDcd + "unsigned_bee_encrypted.png"
        elif txt == 'Yes':
            self.isCertEnabledForBee = True
            self.m_button_genImage.SetLabel('Generate Signed Bootable Image')
            imgPath = "../img/nor_image_" + strHasDcd + "signed_bee_encrypted.png"
        else:
            pass
        self.showImageLayout(imgPath.encode('utf-8'))
        self.m_button_flashImage.SetLabel('Load Encrypted Image')
        self._resetCertificateColor()
        if self.isCertEnabledForBee:
            activeColor = None
            if self.keyStorageRegion == uidef.kKeyStorageRegion_FixedOtpmkKey:
                activeColor = uidef.kBootSeqColor_Active
            elif self.keyStorageRegion == uidef.kKeyStorageRegion_FlexibleUserKeys:
                activeColor = uidef.kBootSeqColor_Optional
            else:
                pass
            self.m_panel_doAuth1_certInput.Enable( True )
            self.m_panel_doAuth1_certInput.SetBackgroundColour( activeColor )
            self.m_textCtrl_serial.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_textCtrl_keyPass.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
            self.m_panel_doAuth2_certFmt.Enable( True )
            self.m_panel_doAuth2_certFmt.SetBackgroundColour( activeColor )
            self.m_button_genCert.Enable( True )
            self.m_button_genCert.SetBackgroundColour( activeColor )
            self.m_panel_progSrk1_showSrk.Enable( True )
            self.m_panel_progSrk1_showSrk.SetBackgroundColour( activeColor )
            self.m_button_progSrk.Enable( True )
            self.m_button_progSrk.SetBackgroundColour( activeColor )
        self.Refresh()

    def setKeyStorageRegionColor( self ):
        self.keyStorageRegion = self.m_choice_keyStorageRegion.GetString(self.m_choice_keyStorageRegion.GetSelection())
        self.toolCommDict['keyStoreRegion'] = self.m_choice_keyStorageRegion.GetSelection()
        self._resetKeyStorageRegionColor()
        self.m_panel_prepBee1_beeKeyRegion.Enable( True )
        self.m_panel_prepBee1_beeKeyRegion.SetBackgroundColour( uidef.kBootSeqColor_Active )
        self.m_panel_prepBee2_beeCryptoAlgo.Enable( True )
        self.m_panel_prepBee2_beeCryptoAlgo.SetBackgroundColour( uidef.kBootSeqColor_Active )
        if self.keyStorageRegion == uidef.kKeyStorageRegion_FixedOtpmkKey:
            self.m_choice_enableCertForBee.Clear()
            self.m_choice_enableCertForBee.SetItems(['Yes'])
            self.m_choice_enableCertForBee.SetSelection(0)
            self.setBeeCertColor()
            self.m_choice_availBeeEngines.Clear()
            self.m_choice_availBeeEngines.SetItems(['1'])
            self.m_choice_availBeeEngines.SetSelection(0)
            self.m_button_prepBee.Enable( True )
            self.m_button_prepBee.SetLabel('Prepare For Encryption')
            self.m_button_prepBee.SetBackgroundColour( uidef.kBootSeqColor_Active )
        elif self.keyStorageRegion == uidef.kKeyStorageRegion_FlexibleUserKeys:
            enableCertForBeeTxt = self.m_choice_enableCertForBee.GetString(self.m_choice_enableCertForBee.GetSelection())
            self.m_choice_enableCertForBee.Clear()
            self.m_choice_enableCertForBee.SetItems(['No', 'Yes'])
            self.m_choice_enableCertForBee.SetSelection(self.m_choice_enableCertForBee.FindString(enableCertForBeeTxt))
            self.setBeeCertColor()
            self.m_choice_availBeeEngines.Clear()
            self.m_choice_availBeeEngines.SetItems(['2'])
            self.m_choice_availBeeEngines.SetSelection(0)
            self.m_button_prepBee.Enable( True )
            self.m_button_prepBee.SetLabel('Encrypt Bootable Image')
            self.m_button_prepBee.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_operBee1_beeKeyInfo.Enable( True )
            self.m_panel_operBee1_beeKeyInfo.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_operBee2_showGp4Dek.Enable( True )
            self.m_panel_operBee2_showGp4Dek.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_panel_operBee3_showSwgp2Dek.Enable( True )
            self.m_panel_operBee3_showSwgp2Dek.SetBackgroundColour( uidef.kBootSeqColor_Active )
            self.m_button_operBee.Enable( True )
            self.m_button_operBee.SetBackgroundColour( uidef.kBootSeqColor_Active )
        else:
            pass
        self.Refresh()

    def popupMsgBox( self, msgStr ):
        messageText = (msgStr.encode('utf-8'))
        wx.MessageBox(messageText, "Error", wx.OK | wx.ICON_INFORMATION)

    def printLog( self, logStr ):
        try:
            self.m_textCtrl_log.write(logStr + "\n")
        except:
            pass

    def clearLog( self ):
        self.m_textCtrl_log.Clear()

    def saveLog( self ):
        self.m_textCtrl_log.SaveFile(self.logFilename)
        msgText = (('Log is saved in file: ' + self.logFilename + ' \n').encode('utf-8'))
        wx.MessageBox(msgText, "Log Info", wx.OK | wx.ICON_INFORMATION)

    def increaseGauge( self, evt ):
        global s_isGaugeWorking
        global s_curGauge
        global s_maxGauge
        if s_isGaugeWorking:
            if s_curGauge < (s_maxGauge - 10):
                self.m_gauge_action.SetValue(s_curGauge)
                s_curGauge += 1
                #wx.CallLater(100, self.increaseGauge)

    def initGauge( self ):
        global s_isGaugeWorking
        global s_curGauge
        global s_maxGauge
        s_isGaugeWorking = True
        s_curGauge = 30
        s_maxGauge = self.m_gauge_action.GetRange()
        self.m_gauge_action.SetValue(s_curGauge)

    def deinitGauge( self ):
        global s_isGaugeWorking
        global s_curGauge
        global s_maxGauge
        s_isGaugeWorking = False
        s_curGauge = s_maxGauge
        self.m_gauge_action.SetValue(s_maxGauge)

    def printDeviceStatus( self, statusStr ):
        self.m_textCtrl_deviceStatus.write(statusStr + "\n")

    def clearDeviceStatus( self ):
        self.m_textCtrl_deviceStatus.Clear()

    def getUserAppFilePath( self ):
        appPath = self.m_filePicker_appPath.GetPath()
        self.toolCommDict['appFilename'] = appPath.encode("utf-8")
        return appPath.encode('utf-8').encode("gbk")

    def _setUserBinaryBaseField( self ):
        txt = self.m_choice_appFormat.GetString(self.m_choice_appFormat.GetSelection())
        if txt == uidef.kAppImageFormat_AutoDetect or txt == uidef.kAppImageFormat_RawBinary:
            self.m_textCtrl_appBaseAddr.Enable(True)
        else:
            self.m_textCtrl_appBaseAddr.Enable(False)

    def getUserAppFileFormat( self ):
        self.toolCommDict['appFormat'] = self.m_choice_appFormat.GetSelection()
        self._setUserBinaryBaseField()
        return self.m_choice_appFormat.GetString(self.m_choice_appFormat.GetSelection())

    def getUserBinaryBaseAddress( self ):
        self.toolCommDict['appBinBaseAddr'] = self.m_textCtrl_appBaseAddr.GetLineText(0)
        return self._getVal32FromHexText(self.m_textCtrl_appBaseAddr.GetLineText(0))

    def printSrkData( self, srkStr ):
        self.m_textCtrl_srk256bit.write(srkStr + "\n")

    def clearSrkData( self ):
        self.m_textCtrl_srk256bit.Clear()

    def printHabDekData( self, dekStr ):
        self.m_textCtrl_habDek128bit.write(dekStr + "\n")

    def clearHabDekData( self ):
        self.m_textCtrl_habDek128bit.Clear()

    def printOtpmkDekData( self, dekStr ):
        #self.m_textCtrl_otpmkDek128bit.write(dekStr + "\n")
        pass

    def clearOtpmkDekData( self ):
        #self.m_textCtrl_otpmkDek128bit.Clear()
        pass

    def printGp4DekData( self, dekStr ):
        self.m_textCtrl_gp4Dek128bit.write(dekStr + "\n")

    def clearGp4DekData( self ):
        self.m_textCtrl_gp4Dek128bit.Clear()

    def printSwGp2DekData( self, dekStr ):
        self.m_textCtrl_swgp2Dek128bit.write(dekStr + "\n")

    def clearSwGp2DekData( self ):
        self.m_textCtrl_swgp2Dek128bit.Clear()

    def _convertLongIntHexText( self, hexText ):
        lastStr = hexText[len(hexText) - 1]
        if lastStr == 'l' or lastStr == 'L':
            return hexText[0:len(hexText) - 1]
        else:
            return hexText

    def _getVal32FromHexText( self, hexText ):
        status = False
        val32 = None
        if len(hexText) > 2 and hexText[0:2] == '0x':
            try:
                val32 = int(hexText[2:len(hexText)], 16)
                status = True
            except:
                pass
        if not status:
            self.popupMsgBox('Illegal input detected! You should input like this format: 0x5000')
        return status, val32

    def getComMemStartAddress( self ):
        return self._getVal32FromHexText(self.m_textCtrl_memStart.GetLineText(0))

    def getComMemByteLength( self ):
        return self._getVal32FromHexText(self.m_textCtrl_memLength.GetLineText(0))

    def getComMemBinFile( self ):
        memBinFile = self.m_filePicker_memBinFile.GetPath()
        return memBinFile.encode('utf-8').encode("gbk")

    def needToSaveReadbackImageData( self ):
        return self.m_checkBox_saveImageData.GetValue()

    def getImageDataFileToSave( self ):
        savedBinFile = self.m_filePicker_savedBinFile.GetPath()
        return savedBinFile.encode('utf-8').encode("gbk")

    def setImageDataFilePath( self, filePath ):
        self.m_filePicker_savedBinFile.SetPath(filePath)

    def printMem( self , memStr, strColor=uidef.kMemBlockColor_Padding ):
        self.m_textCtrl_bootDeviceMem.SetDefaultStyle(wx.TextAttr(strColor, uidef.kMemBlockColor_Background))
        self.m_textCtrl_bootDeviceMem.AppendText(memStr + "\n")

    def clearMem( self ):
        self.m_textCtrl_bootDeviceMem.Clear()

    def showImageLayout( self , imgPath ):
        self.m_bitmap_bootableImage.SetBitmap(wx.Bitmap( imgPath, wx.BITMAP_TYPE_ANY ))

    def updateFuseRegionField( self ):
        color = None
        if self.isToolRunAsEntryMode:
            color = wx.SYS_COLOUR_GRAYTEXT
        else:
            color = wx.SYS_COLOUR_WINDOW
        self.m_textCtrl_fuse400.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )

        self.m_textCtrl_fuse430.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse440.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )

        self.m_textCtrl_fuse480.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse490.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4a0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4b0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4c0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4d0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4e0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse4f0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse500.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse510.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse520.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse530.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse540.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse550.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse560.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse570.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )

        self.m_textCtrl_fuse600.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse610.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse620.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse630.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse640.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse650.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse660.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse670.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse680.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )

        self.m_textCtrl_fuse6f0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse700.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse710.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse720.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse730.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse740.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse750.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse760.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse770.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse780.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse790.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7a0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7b0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7c0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7d0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7e0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse7f0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse800.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse810.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse820.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse830.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse840.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse850.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse860.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse870.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse880.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse890.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse8a0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.m_textCtrl_fuse8b0.SetBackgroundColour( wx.SystemSettings.GetColour( color ) )
        self.Refresh()

    def getFormattedFuseValue( self, fuseValue, direction='LSB'):
        formattedVal32 = ''
        for i in range(8):
            loc = 0
            if direction =='LSB':
                loc = 32 - (i + 1) * 4
            elif direction =='MSB':
                loc = i * 4
            else:
                pass
            halfbyteStr = str(hex((fuseValue & (0xF << loc))>> loc))
            formattedVal32 += halfbyteStr[2]
        return formattedVal32

    def getFormattedHexValue( self, val32 ):
        return ('0x' + self.getFormattedFuseValue(val32))

    def _parseReadFuseValue( self, fuseValue ):
        if fuseValue != None:
            return self.getFormattedHexValue(fuseValue)
        else:
            return '--------'

    def showScannedFuses( self , scannedFuseList ):
        self.m_textCtrl_fuse400.Clear()
        self.m_textCtrl_fuse400.write(self._parseReadFuseValue(scannedFuseList[0]))
        self.m_textCtrl_fuse410.Clear()
        self.m_textCtrl_fuse410.write(self._parseReadFuseValue(scannedFuseList[1]))
        self.m_textCtrl_fuse420.Clear()
        self.m_textCtrl_fuse420.write(self._parseReadFuseValue(scannedFuseList[2]))
        self.m_textCtrl_fuse430.Clear()
        self.m_textCtrl_fuse430.write(self._parseReadFuseValue(scannedFuseList[3]))
        self.m_textCtrl_fuse440.Clear()
        self.m_textCtrl_fuse440.write(self._parseReadFuseValue(scannedFuseList[4]))
        self.m_textCtrl_fuse450.Clear()
        self.m_textCtrl_fuse450.write(self._parseReadFuseValue(scannedFuseList[5]))
        self.m_textCtrl_fuse460.Clear()
        self.m_textCtrl_fuse460.write(self._parseReadFuseValue(scannedFuseList[6]))
        self.m_textCtrl_fuse470.Clear()
        self.m_textCtrl_fuse470.write(self._parseReadFuseValue(scannedFuseList[7]))
        self.m_textCtrl_fuse480.Clear()
        self.m_textCtrl_fuse480.write(self._parseReadFuseValue(scannedFuseList[8]))
        self.m_textCtrl_fuse490.Clear()
        self.m_textCtrl_fuse490.write(self._parseReadFuseValue(scannedFuseList[9]))
        self.m_textCtrl_fuse4a0.Clear()
        self.m_textCtrl_fuse4a0.write(self._parseReadFuseValue(scannedFuseList[10]))
        self.m_textCtrl_fuse4b0.Clear()
        self.m_textCtrl_fuse4b0.write(self._parseReadFuseValue(scannedFuseList[11]))
        self.m_textCtrl_fuse4c0.Clear()
        self.m_textCtrl_fuse4c0.write(self._parseReadFuseValue(scannedFuseList[12]))
        self.m_textCtrl_fuse4d0.Clear()
        self.m_textCtrl_fuse4d0.write(self._parseReadFuseValue(scannedFuseList[13]))
        self.m_textCtrl_fuse4e0.Clear()
        self.m_textCtrl_fuse4e0.write(self._parseReadFuseValue(scannedFuseList[14]))
        self.m_textCtrl_fuse4f0.Clear()
        self.m_textCtrl_fuse4f0.write(self._parseReadFuseValue(scannedFuseList[15]))

        self.m_textCtrl_fuse500.Clear()
        self.m_textCtrl_fuse500.write(self._parseReadFuseValue(scannedFuseList[16]))
        self.m_textCtrl_fuse510.Clear()
        self.m_textCtrl_fuse510.write(self._parseReadFuseValue(scannedFuseList[17]))
        self.m_textCtrl_fuse520.Clear()
        self.m_textCtrl_fuse520.write(self._parseReadFuseValue(scannedFuseList[18]))
        self.m_textCtrl_fuse530.Clear()
        self.m_textCtrl_fuse530.write(self._parseReadFuseValue(scannedFuseList[19]))
        self.m_textCtrl_fuse540.Clear()
        self.m_textCtrl_fuse540.write(self._parseReadFuseValue(scannedFuseList[20]))
        self.m_textCtrl_fuse550.Clear()
        self.m_textCtrl_fuse550.write(self._parseReadFuseValue(scannedFuseList[21]))
        self.m_textCtrl_fuse560.Clear()
        self.m_textCtrl_fuse560.write(self._parseReadFuseValue(scannedFuseList[22]))
        self.m_textCtrl_fuse570.Clear()
        self.m_textCtrl_fuse570.write(self._parseReadFuseValue(scannedFuseList[23]))
        self.m_textCtrl_fuse580.Clear()
        self.m_textCtrl_fuse580.write(self._parseReadFuseValue(scannedFuseList[24]))
        self.m_textCtrl_fuse590.Clear()
        self.m_textCtrl_fuse590.write(self._parseReadFuseValue(scannedFuseList[25]))
        self.m_textCtrl_fuse5a0.Clear()
        self.m_textCtrl_fuse5a0.write(self._parseReadFuseValue(scannedFuseList[26]))
        self.m_textCtrl_fuse5b0.Clear()
        self.m_textCtrl_fuse5b0.write(self._parseReadFuseValue(scannedFuseList[27]))
        self.m_textCtrl_fuse5c0.Clear()
        self.m_textCtrl_fuse5c0.write(self._parseReadFuseValue(scannedFuseList[28]))
        self.m_textCtrl_fuse5d0.Clear()
        self.m_textCtrl_fuse5d0.write(self._parseReadFuseValue(scannedFuseList[29]))
        self.m_textCtrl_fuse5e0.Clear()
        self.m_textCtrl_fuse5e0.write(self._parseReadFuseValue(scannedFuseList[30]))
        self.m_textCtrl_fuse5f0.Clear()
        self.m_textCtrl_fuse5f0.write(self._parseReadFuseValue(scannedFuseList[31]))

        self.m_textCtrl_fuse600.Clear()
        self.m_textCtrl_fuse600.write(self._parseReadFuseValue(scannedFuseList[32]))
        self.m_textCtrl_fuse610.Clear()
        self.m_textCtrl_fuse610.write(self._parseReadFuseValue(scannedFuseList[33]))
        self.m_textCtrl_fuse620.Clear()
        self.m_textCtrl_fuse620.write(self._parseReadFuseValue(scannedFuseList[34]))
        self.m_textCtrl_fuse630.Clear()
        self.m_textCtrl_fuse630.write(self._parseReadFuseValue(scannedFuseList[35]))
        self.m_textCtrl_fuse640.Clear()
        self.m_textCtrl_fuse640.write(self._parseReadFuseValue(scannedFuseList[36]))
        self.m_textCtrl_fuse650.Clear()
        self.m_textCtrl_fuse650.write(self._parseReadFuseValue(scannedFuseList[37]))
        self.m_textCtrl_fuse660.Clear()
        self.m_textCtrl_fuse660.write(self._parseReadFuseValue(scannedFuseList[38]))
        self.m_textCtrl_fuse670.Clear()
        self.m_textCtrl_fuse670.write(self._parseReadFuseValue(scannedFuseList[39]))
        self.m_textCtrl_fuse680.Clear()
        self.m_textCtrl_fuse680.write(self._parseReadFuseValue(scannedFuseList[40]))
        self.m_textCtrl_fuse690.Clear()
        self.m_textCtrl_fuse690.write(self._parseReadFuseValue(scannedFuseList[41]))
        self.m_textCtrl_fuse6a0.Clear()
        self.m_textCtrl_fuse6a0.write(self._parseReadFuseValue(scannedFuseList[42]))
        self.m_textCtrl_fuse6b0.Clear()
        self.m_textCtrl_fuse6b0.write(self._parseReadFuseValue(scannedFuseList[43]))
        self.m_textCtrl_fuse6c0.Clear()
        self.m_textCtrl_fuse6c0.write(self._parseReadFuseValue(scannedFuseList[44]))
        self.m_textCtrl_fuse6d0.Clear()
        self.m_textCtrl_fuse6d0.write(self._parseReadFuseValue(scannedFuseList[45]))
        self.m_textCtrl_fuse6e0.Clear()
        self.m_textCtrl_fuse6e0.write(self._parseReadFuseValue(scannedFuseList[46]))
        self.m_textCtrl_fuse6f0.Clear()
        self.m_textCtrl_fuse6f0.write(self._parseReadFuseValue(scannedFuseList[47]))

        self.m_textCtrl_fuse700.Clear()
        self.m_textCtrl_fuse700.write(self._parseReadFuseValue(scannedFuseList[48]))
        self.m_textCtrl_fuse710.Clear()
        self.m_textCtrl_fuse710.write(self._parseReadFuseValue(scannedFuseList[49]))
        self.m_textCtrl_fuse720.Clear()
        self.m_textCtrl_fuse720.write(self._parseReadFuseValue(scannedFuseList[50]))
        self.m_textCtrl_fuse730.Clear()
        self.m_textCtrl_fuse730.write(self._parseReadFuseValue(scannedFuseList[51]))
        self.m_textCtrl_fuse740.Clear()
        self.m_textCtrl_fuse740.write(self._parseReadFuseValue(scannedFuseList[52]))
        self.m_textCtrl_fuse750.Clear()
        self.m_textCtrl_fuse750.write(self._parseReadFuseValue(scannedFuseList[53]))
        self.m_textCtrl_fuse760.Clear()
        self.m_textCtrl_fuse760.write(self._parseReadFuseValue(scannedFuseList[54]))
        self.m_textCtrl_fuse770.Clear()
        self.m_textCtrl_fuse770.write(self._parseReadFuseValue(scannedFuseList[55]))
        self.m_textCtrl_fuse780.Clear()
        self.m_textCtrl_fuse780.write(self._parseReadFuseValue(scannedFuseList[56]))
        self.m_textCtrl_fuse790.Clear()
        self.m_textCtrl_fuse790.write(self._parseReadFuseValue(scannedFuseList[57]))
        self.m_textCtrl_fuse7a0.Clear()
        self.m_textCtrl_fuse7a0.write(self._parseReadFuseValue(scannedFuseList[58]))
        self.m_textCtrl_fuse7b0.Clear()
        self.m_textCtrl_fuse7b0.write(self._parseReadFuseValue(scannedFuseList[59]))
        self.m_textCtrl_fuse7c0.Clear()
        self.m_textCtrl_fuse7c0.write(self._parseReadFuseValue(scannedFuseList[60]))
        self.m_textCtrl_fuse7d0.Clear()
        self.m_textCtrl_fuse7d0.write(self._parseReadFuseValue(scannedFuseList[61]))
        self.m_textCtrl_fuse7e0.Clear()
        self.m_textCtrl_fuse7e0.write(self._parseReadFuseValue(scannedFuseList[62]))
        self.m_textCtrl_fuse7f0.Clear()
        self.m_textCtrl_fuse7f0.write(self._parseReadFuseValue(scannedFuseList[63]))

        self.m_textCtrl_fuse800.Clear()
        self.m_textCtrl_fuse800.write(self._parseReadFuseValue(scannedFuseList[64]))
        self.m_textCtrl_fuse810.Clear()
        self.m_textCtrl_fuse810.write(self._parseReadFuseValue(scannedFuseList[65]))
        self.m_textCtrl_fuse820.Clear()
        self.m_textCtrl_fuse820.write(self._parseReadFuseValue(scannedFuseList[66]))
        self.m_textCtrl_fuse830.Clear()
        self.m_textCtrl_fuse830.write(self._parseReadFuseValue(scannedFuseList[67]))
        self.m_textCtrl_fuse840.Clear()
        self.m_textCtrl_fuse840.write(self._parseReadFuseValue(scannedFuseList[68]))
        self.m_textCtrl_fuse850.Clear()
        self.m_textCtrl_fuse850.write(self._parseReadFuseValue(scannedFuseList[69]))
        self.m_textCtrl_fuse860.Clear()
        self.m_textCtrl_fuse860.write(self._parseReadFuseValue(scannedFuseList[70]))
        self.m_textCtrl_fuse870.Clear()
        self.m_textCtrl_fuse870.write(self._parseReadFuseValue(scannedFuseList[71]))
        self.m_textCtrl_fuse880.Clear()
        self.m_textCtrl_fuse880.write(self._parseReadFuseValue(scannedFuseList[72]))
        self.m_textCtrl_fuse890.Clear()
        self.m_textCtrl_fuse890.write(self._parseReadFuseValue(scannedFuseList[73]))
        self.m_textCtrl_fuse8a0.Clear()
        self.m_textCtrl_fuse8a0.write(self._parseReadFuseValue(scannedFuseList[74]))
        self.m_textCtrl_fuse8b0.Clear()
        self.m_textCtrl_fuse8b0.write(self._parseReadFuseValue(scannedFuseList[75]))
        self.m_textCtrl_fuse8c0.Clear()
        self.m_textCtrl_fuse8c0.write(self._parseReadFuseValue(scannedFuseList[76]))
        self.m_textCtrl_fuse8d0.Clear()
        self.m_textCtrl_fuse8d0.write(self._parseReadFuseValue(scannedFuseList[77]))
        self.m_textCtrl_fuse8e0.Clear()
        self.m_textCtrl_fuse8e0.write(self._parseReadFuseValue(scannedFuseList[78]))
        self.m_textCtrl_fuse8f0.Clear()
        self.m_textCtrl_fuse8f0.write(self._parseReadFuseValue(scannedFuseList[79]))

    def _parseUserFuseValue( self, fuseText ):
        if len(fuseText) >= 3 and fuseText[0:2] == '0x':
            return int(fuseText[2:len(fuseText)], 16)
        else:
            return None

    def getUserFuses( self ):
        userFuseList = [None] * fusedef.kMaxEfuseWords
        userFuseList[0] = self._parseUserFuseValue(self.m_textCtrl_fuse400.GetLineText(0))
        userFuseList[1] = self._parseUserFuseValue(self.m_textCtrl_fuse410.GetLineText(0))
        userFuseList[2] = self._parseUserFuseValue(self.m_textCtrl_fuse420.GetLineText(0))
        userFuseList[3] = self._parseUserFuseValue(self.m_textCtrl_fuse430.GetLineText(0))
        userFuseList[4] = self._parseUserFuseValue(self.m_textCtrl_fuse440.GetLineText(0))
        userFuseList[5] = self._parseUserFuseValue(self.m_textCtrl_fuse450.GetLineText(0))
        userFuseList[6] = self._parseUserFuseValue(self.m_textCtrl_fuse460.GetLineText(0))
        userFuseList[7] = self._parseUserFuseValue(self.m_textCtrl_fuse470.GetLineText(0))
        userFuseList[8] = self._parseUserFuseValue(self.m_textCtrl_fuse480.GetLineText(0))
        userFuseList[9] = self._parseUserFuseValue(self.m_textCtrl_fuse490.GetLineText(0))
        userFuseList[10] = self._parseUserFuseValue(self.m_textCtrl_fuse4a0.GetLineText(0))
        userFuseList[11] = self._parseUserFuseValue(self.m_textCtrl_fuse4b0.GetLineText(0))
        userFuseList[12] = self._parseUserFuseValue(self.m_textCtrl_fuse4c0.GetLineText(0))
        userFuseList[13] = self._parseUserFuseValue(self.m_textCtrl_fuse4d0.GetLineText(0))
        userFuseList[14] = self._parseUserFuseValue(self.m_textCtrl_fuse4e0.GetLineText(0))
        userFuseList[15] = self._parseUserFuseValue(self.m_textCtrl_fuse4f0.GetLineText(0))

        userFuseList[16] = self._parseUserFuseValue(self.m_textCtrl_fuse500.GetLineText(0))
        userFuseList[17] = self._parseUserFuseValue(self.m_textCtrl_fuse510.GetLineText(0))
        userFuseList[18] = self._parseUserFuseValue(self.m_textCtrl_fuse520.GetLineText(0))
        userFuseList[19] = self._parseUserFuseValue(self.m_textCtrl_fuse530.GetLineText(0))
        userFuseList[20] = self._parseUserFuseValue(self.m_textCtrl_fuse540.GetLineText(0))
        userFuseList[21] = self._parseUserFuseValue(self.m_textCtrl_fuse550.GetLineText(0))
        userFuseList[22] = self._parseUserFuseValue(self.m_textCtrl_fuse560.GetLineText(0))
        userFuseList[23] = self._parseUserFuseValue(self.m_textCtrl_fuse570.GetLineText(0))
        userFuseList[24] = self._parseUserFuseValue(self.m_textCtrl_fuse580.GetLineText(0))
        userFuseList[25] = self._parseUserFuseValue(self.m_textCtrl_fuse590.GetLineText(0))
        userFuseList[26] = self._parseUserFuseValue(self.m_textCtrl_fuse5a0.GetLineText(0))
        userFuseList[27] = self._parseUserFuseValue(self.m_textCtrl_fuse5b0.GetLineText(0))
        userFuseList[28] = self._parseUserFuseValue(self.m_textCtrl_fuse5c0.GetLineText(0))
        userFuseList[29] = self._parseUserFuseValue(self.m_textCtrl_fuse5d0.GetLineText(0))
        userFuseList[30] = self._parseUserFuseValue(self.m_textCtrl_fuse5e0.GetLineText(0))
        userFuseList[31] = self._parseUserFuseValue(self.m_textCtrl_fuse5f0.GetLineText(0))

        userFuseList[32] = self._parseUserFuseValue(self.m_textCtrl_fuse600.GetLineText(0))
        userFuseList[33] = self._parseUserFuseValue(self.m_textCtrl_fuse610.GetLineText(0))
        userFuseList[34] = self._parseUserFuseValue(self.m_textCtrl_fuse620.GetLineText(0))
        userFuseList[35] = self._parseUserFuseValue(self.m_textCtrl_fuse630.GetLineText(0))
        userFuseList[36] = self._parseUserFuseValue(self.m_textCtrl_fuse640.GetLineText(0))
        userFuseList[37] = self._parseUserFuseValue(self.m_textCtrl_fuse650.GetLineText(0))
        userFuseList[38] = self._parseUserFuseValue(self.m_textCtrl_fuse660.GetLineText(0))
        userFuseList[39] = self._parseUserFuseValue(self.m_textCtrl_fuse670.GetLineText(0))
        userFuseList[40] = self._parseUserFuseValue(self.m_textCtrl_fuse680.GetLineText(0))
        userFuseList[41] = self._parseUserFuseValue(self.m_textCtrl_fuse690.GetLineText(0))
        userFuseList[42] = self._parseUserFuseValue(self.m_textCtrl_fuse6a0.GetLineText(0))
        userFuseList[43] = self._parseUserFuseValue(self.m_textCtrl_fuse6b0.GetLineText(0))
        userFuseList[44] = self._parseUserFuseValue(self.m_textCtrl_fuse6c0.GetLineText(0))
        userFuseList[45] = self._parseUserFuseValue(self.m_textCtrl_fuse6d0.GetLineText(0))
        userFuseList[46] = self._parseUserFuseValue(self.m_textCtrl_fuse6e0.GetLineText(0))
        userFuseList[47] = self._parseUserFuseValue(self.m_textCtrl_fuse6f0.GetLineText(0))

        userFuseList[48] = self._parseUserFuseValue(self.m_textCtrl_fuse700.GetLineText(0))
        userFuseList[49] = self._parseUserFuseValue(self.m_textCtrl_fuse710.GetLineText(0))
        userFuseList[50] = self._parseUserFuseValue(self.m_textCtrl_fuse720.GetLineText(0))
        userFuseList[51] = self._parseUserFuseValue(self.m_textCtrl_fuse730.GetLineText(0))
        userFuseList[52] = self._parseUserFuseValue(self.m_textCtrl_fuse730.GetLineText(0))
        userFuseList[53] = self._parseUserFuseValue(self.m_textCtrl_fuse750.GetLineText(0))
        userFuseList[54] = self._parseUserFuseValue(self.m_textCtrl_fuse760.GetLineText(0))
        userFuseList[55] = self._parseUserFuseValue(self.m_textCtrl_fuse770.GetLineText(0))
        userFuseList[56] = self._parseUserFuseValue(self.m_textCtrl_fuse780.GetLineText(0))
        userFuseList[57] = self._parseUserFuseValue(self.m_textCtrl_fuse790.GetLineText(0))
        userFuseList[58] = self._parseUserFuseValue(self.m_textCtrl_fuse7a0.GetLineText(0))
        userFuseList[59] = self._parseUserFuseValue(self.m_textCtrl_fuse7b0.GetLineText(0))
        userFuseList[60] = self._parseUserFuseValue(self.m_textCtrl_fuse7c0.GetLineText(0))
        userFuseList[61] = self._parseUserFuseValue(self.m_textCtrl_fuse7d0.GetLineText(0))
        userFuseList[62] = self._parseUserFuseValue(self.m_textCtrl_fuse7e0.GetLineText(0))
        userFuseList[63] = self._parseUserFuseValue(self.m_textCtrl_fuse7f0.GetLineText(0))

        userFuseList[64] = self._parseUserFuseValue(self.m_textCtrl_fuse800.GetLineText(0))
        userFuseList[65] = self._parseUserFuseValue(self.m_textCtrl_fuse810.GetLineText(0))
        userFuseList[66] = self._parseUserFuseValue(self.m_textCtrl_fuse820.GetLineText(0))
        userFuseList[67] = self._parseUserFuseValue(self.m_textCtrl_fuse830.GetLineText(0))
        userFuseList[68] = self._parseUserFuseValue(self.m_textCtrl_fuse840.GetLineText(0))
        userFuseList[69] = self._parseUserFuseValue(self.m_textCtrl_fuse850.GetLineText(0))
        userFuseList[70] = self._parseUserFuseValue(self.m_textCtrl_fuse860.GetLineText(0))
        userFuseList[71] = self._parseUserFuseValue(self.m_textCtrl_fuse870.GetLineText(0))
        userFuseList[72] = self._parseUserFuseValue(self.m_textCtrl_fuse880.GetLineText(0))
        userFuseList[73] = self._parseUserFuseValue(self.m_textCtrl_fuse890.GetLineText(0))
        userFuseList[74] = self._parseUserFuseValue(self.m_textCtrl_fuse8a0.GetLineText(0))
        userFuseList[75] = self._parseUserFuseValue(self.m_textCtrl_fuse8b0.GetLineText(0))
        userFuseList[76] = self._parseUserFuseValue(self.m_textCtrl_fuse8c0.GetLineText(0))
        userFuseList[77] = self._parseUserFuseValue(self.m_textCtrl_fuse8d0.GetLineText(0))
        userFuseList[78] = self._parseUserFuseValue(self.m_textCtrl_fuse8e0.GetLineText(0))
        userFuseList[79] = self._parseUserFuseValue(self.m_textCtrl_fuse8f0.GetLineText(0))

        return userFuseList

