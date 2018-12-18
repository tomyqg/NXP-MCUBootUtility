#! /usr/bin/env python
import sys
import os
import json
import uidef

g_cfgFilename = None
g_toolCommDict = {'isToolRunAsEntryMode':None,
                  'secBootType':None,
                  'mcuSeries':None,
                  'mcuDevice':None,
                  'bootDevice':None,
                  'isUsbhidPortSelected':None,
                  'isOneStepChecked':None,
                  'certSerial':None,
                  'certKeyPass':None,
                  'appFilename':None,
                  'appFormat':None,
                  'appBinBaseAddr':None,
                  'keyStoreRegion':None,
                  'certOptForBee':None
                 }

g_flexspiNorOpt0 = None
g_flexspiNorOpt1 = None
g_flexspiNorDeviceModel = None

g_flexspiNandOpt = None
g_flexspiNandFcbOpt = None
g_flexspiNandImageInfo = None
g_flexspiNandKeyBlob = None

g_semcNorOpt = None
g_semcNorSetting = None

g_semcNandOpt = None
g_semcNandFcbOpt = None
g_semcNandImageInfo = None

g_usdhcSdOpt = None

g_usdhcMmcOpt1 = None
g_usdhcMmcOpt2 = None

g_lpspiNorOpt0 = None
g_lpspiNorOpt1 = None

g_certSettingsDict = {'cstVersion':None,
                      'useExistingCaKey':None,
                      'useEllipticCurveCrypto':None,
                      'pkiTreeKeyLen':None,
                      'pkiTreeKeyCn':None,
                      'pkiTreeDuration':None,
                      'SRKs':None,
                      'caFlagSet':None}

g_otpmkKeyOpt = None
g_otpmkEncryptedRegionStart = None
g_otpmkEncryptedRegionLength = None

g_userKeyCtrlDict = {'mcu_device':None,
                     'engine_sel':None,
                     'engine0_key_src':None,
                     'engine0_fac_cnt':None,
                     'engine1_key_src':None,
                     'engine1_fac_cnt':None}
g_userKeyCmdDict = {'base_addr':None,
                    'engine0_key':None,
                    'engine0_arg':None,
                    'engine0_lock':None,
                    'engine1_key':None,
                    'engine1_arg':None,
                    'engine1_lock':None,
                    'use_zero_key':None,
                    'is_boot_image':None}

def initVar(cfgFilename):
    global g_cfgFilename
    g_cfgFilename = cfgFilename
    if os.path.isfile(cfgFilename):
        cfgDict = None
        with open(cfgFilename, 'r') as fileObj:
            cfgDict = json.load(fileObj)
            global g_toolCommDict
            g_toolCommDict = cfgDict["cfgToolCommon"][0]

            global g_flexspiNorOpt0
            global g_flexspiNorOpt1
            global g_flexspiNorDeviceModel
            g_flexspiNorOpt0 = cfgDict["cfgFlexspiNor"][0]
            g_flexspiNorOpt1 = cfgDict["cfgFlexspiNor"][1]
            g_flexspiNorDeviceModel = cfgDict["cfgFlexspiNor"][2]

            global g_semcNandOpt
            global g_semcNandFcbOpt
            global g_semcNandImageInfo
            g_semcNandOpt = cfgDict["cfgSemcNand"][0]
            g_semcNandFcbOpt = cfgDict["cfgSemcNand"][1]
            g_semcNandImageInfo = cfgDict["cfgSemcNand"][2]

            global g_lpspiNorOpt0
            global g_lpspiNorOpt1
            g_lpspiNorOpt0 = cfgDict["cfgLpspiNor"][0]
            g_lpspiNorOpt1 = cfgDict["cfgLpspiNor"][1]

            global g_certSettingsDict
            g_certSettingsDict = cfgDict["cfgCertificate"][0]

            global g_otpmkKeyOpt
            global g_otpmkEncryptedRegionStart
            global g_otpmkEncryptedRegionLength
            g_otpmkKeyOpt = cfgDict["cfgSnvsKey"][0]
            g_otpmkEncryptedRegionStart = cfgDict["cfgSnvsKey"][1]
            g_otpmkEncryptedRegionLength = cfgDict["cfgSnvsKey"][2]

            global g_userKeyCtrlDict
            global g_userKeyCmdDict
            g_userKeyCtrlDict = cfgDict["cfgUserKey"][0]
            g_userKeyCmdDict = cfgDict["cfgUserKey"][1]

            fileObj.close()
    else:
        global g_toolCommDict
        g_toolCommDict = {'isToolRunAsEntryMode':True,
                          'secBootType':0,
                          'mcuSeries':0,
                          'mcuDevice':1,
                          'bootDevice':0,
                          'isUsbhidPortSelected':True,
                          'isOneStepChecked':True,
                          'certSerial':'12345678',
                          'certKeyPass':'test',
                          'appFilename':None,
                          'appFormat':0,
                          'appBinBaseAddr':'0x00003000',
                          'keyStoreRegion':1,
                          'certOptForBee':0
                         }

        global g_flexspiNorOpt0
        global g_flexspiNorOpt1
        global g_flexspiNorDeviceModel
        g_flexspiNorOpt0 = 0xc0000007
        g_flexspiNorOpt1 = 0x00000000
        g_flexspiNorDeviceModel = 0

        global g_flexspiNandOpt
        global g_flexspiNandFcbOpt
        global g_flexspiNandKeyBlob
        global g_flexspiNandImageInfo
        g_flexspiNandOpt = 0xD0010101
        g_flexspiNandFcbOpt = 0x00010601
        g_flexspiNandImageInfo = 0x0
        g_flexspiNandKeyBlob = 0x0

        global g_semcNorOpt
        global g_semcNorSetting
        g_semcNorOpt = 0xD0010101
        g_semcNorSetting = 0x00010601

        global g_semcNandOpt
        global g_semcNandFcbOpt
        global g_semcNandImageInfo
        g_semcNandOpt = 0xD0010101
        g_semcNandFcbOpt = 0x00010101
        g_semcNandImageInfo = [None] * 8
        g_semcNandImageInfo[0] = 0x00020001

        global g_usdhcSdOpt
        g_usdhcSdOpt = 0xD0010101

        global g_usdhcMmcOpt1
        global g_usdhcMmcOpt2
        g_usdhcMmcOpt1 = 0xD0010101
        g_usdhcMmcOpt2 = 0xD0010101

        global g_lpspiNorOpt0
        global g_lpspiNorOpt1
        g_lpspiNorOpt0 = 0xc1100500
        g_lpspiNorOpt1 = 0x00000000

        global g_certSettingsDict
        g_certSettingsDict['cstVersion'] = uidef.kCstVersion_v3_0_1
        g_certSettingsDict['useExistingCaKey'] = 'n'
        g_certSettingsDict['useEllipticCurveCrypto'] = 'n'
        g_certSettingsDict['pkiTreeKeyLen'] = 2048
        g_certSettingsDict['pkiTreeDuration'] = 10
        g_certSettingsDict['SRKs'] = 4
        g_certSettingsDict['caFlagSet'] = 'y'

        global g_otpmkKeyOpt
        global g_otpmkEncryptedRegionStart
        global g_otpmkEncryptedRegionLength
        g_otpmkKeyOpt = 0xe0100000
        g_otpmkEncryptedRegionStart = [None] * 3
        g_otpmkEncryptedRegionLength = [None] * 3

        global g_userKeyCtrlDict
        global g_userKeyCmdDict
        g_userKeyCtrlDict['engine_sel'] = uidef.kUserEngineSel_Engine0
        g_userKeyCtrlDict['engine0_key_src'] = uidef.kUserKeySource_SW_GP2
        g_userKeyCtrlDict['engine0_fac_cnt'] = 1
        g_userKeyCtrlDict['engine1_key_src'] = uidef.kUserKeySource_SW_GP2
        g_userKeyCtrlDict['engine1_fac_cnt'] = 1
        g_userKeyCmdDict['base_addr'] = '0x60000000'
        g_userKeyCmdDict['engine0_key'] = '0123456789abcdeffedcba9876543210'
        g_userKeyCmdDict['engine0_arg'] = '1,[0x60001000,0x1000,0]'
        g_userKeyCmdDict['engine0_lock'] = '0'
        g_userKeyCmdDict['engine1_key'] = '0123456789abcdeffedcba9876543210'
        g_userKeyCmdDict['engine1_arg'] = '1,[0x60002000,0x1000,0]'
        g_userKeyCmdDict['engine1_lock'] = '0'
        g_userKeyCmdDict['use_zero_key'] = '1'
        g_userKeyCmdDict['is_boot_image'] = '1'

def deinitVar(cfgFilename=None):
    global g_cfgFilename
    if cfgFilename == None and g_cfgFilename != None:
        cfgFilename = g_cfgFilename
    with open(cfgFilename, 'w') as fileObj:
        global g_toolCommDict
        global g_flexspiNorOpt0
        global g_flexspiNorOpt1
        global g_flexspiNorDeviceModel
        global g_semcNandOpt
        global g_semcNandFcbOpt
        global g_semcNandImageInfo
        global g_lpspiNorOpt0
        global g_lpspiNorOpt1
        global g_certSettingsDict
        global g_otpmkKeyOpt
        global g_otpmkEncryptedRegionStart
        global g_otpmkEncryptedRegionLength
        global g_userKeyCtrlDict
        global g_userKeyCmdDict
        cfgDict = {
            "cfgToolCommon": [g_toolCommDict],
            "cfgFlexspiNor": [g_flexspiNorOpt0, g_flexspiNorOpt1, g_flexspiNorDeviceModel],
            "cfgSemcNand": [g_semcNandOpt, g_semcNandFcbOpt, g_semcNandImageInfo],
            "cfgLpspiNor": [g_lpspiNorOpt0, g_lpspiNorOpt1],
            "cfgCertificate": [g_certSettingsDict],
            "cfgSnvsKey": [g_otpmkKeyOpt, g_otpmkEncryptedRegionStart, g_otpmkEncryptedRegionLength],
            "cfgUserKey": [g_userKeyCtrlDict, g_userKeyCmdDict]
        }
        json.dump(cfgDict, fileObj)
        fileObj.close()

def getBootDeviceConfiguration( group ):
    if group == uidef.kBootDevice_FlexspiNor:
        global g_flexspiNorOpt0
        global g_flexspiNorOpt1
        global g_flexspiNorDeviceModel
        return g_flexspiNorOpt0, g_flexspiNorOpt1, g_flexspiNorDeviceModel
    elif group == uidef.kBootDevice_FlexspiNand:
        global g_flexspiNandOpt
        global g_flexspiNandFcbOpt
        global g_flexspiNandKeyBlob
        global g_flexspiNandImageInfo
        return g_flexspiNandOpt, g_flexspiNandFcbOpt, g_flexspiNandImageInfo, g_flexspiNandKeyBlob
    elif group == uidef.kBootDevice_SemcNor:
        global g_semcNorOpt
        global g_semcNorSetting
        return g_semcNorOpt, g_semcNorSetting
    elif group == uidef.kBootDevice_SemcNand:
        global g_semcNandOpt
        global g_semcNandFcbOpt
        global g_semcNandImageInfo
        return g_semcNandOpt, g_semcNandFcbOpt, g_semcNandImageInfo
    elif group == uidef.kBootDevice_UsdhcSd:
        global g_usdhcSdOpt
        return g_usdhcSdOpt
    elif group == uidef.kBootDevice_UsdhcMmc:
        global g_usdhcMmcOpt1
        global g_usdhcMmcOpt2
        return g_usdhcMmcOpt1, g_usdhcMmcOpt2
    elif group == uidef.kBootDevice_LpspiNor:
        global g_lpspiNorOpt0
        global g_lpspiNorOpt1
        return g_lpspiNorOpt0, g_lpspiNorOpt1
    else:
        pass

def setBootDeviceConfiguration( group, *args ):
    if group == uidef.kBootDevice_FlexspiNor:
        global g_flexspiNorOpt0
        global g_flexspiNorOpt1
        global g_flexspiNorDeviceModel
        g_flexspiNorOpt0 = args[0]
        g_flexspiNorOpt1 = args[1]
        g_flexspiNorDeviceModel = args[2]
    elif group == uidef.kBootDevice_FlexspiNand:
        global g_flexspiNandOpt
        global g_flexspiNandFcbOpt
        global g_flexspiNandKeyBlob
        global g_flexspiNandImageInfo
        g_flexspiNandOpt = args[0]
        g_flexspiNandFcbOpt = args[1]
        g_flexspiNandImageInfo = args[2]
        g_flexspiNandKeyBlob = args[3]
    elif group == uidef.kBootDevice_SemcNor:
        global g_semcNorOpt
        global g_semcNorSetting
        g_semcNorOpt = args[0]
        g_semcNorSetting = args[1]
    elif group == uidef.kBootDevice_SemcNand:
        global g_semcNandOpt
        global g_semcNandFcbOpt
        global g_semcNandImageInfo
        g_semcNandOpt = args[0]
        g_semcNandFcbOpt = args[1]
        g_semcNandImageInfo = args[2]
    elif group == uidef.kBootDevice_UsdhcSd:
        global g_usdhcSdOpt
        g_usdhcSdOpt = args[0]
    elif group == uidef.kBootDevice_UsdhcMmc:
        global g_usdhcMmcOpt1
        global g_usdhcMmcOpt2
        g_usdhcMmcOpt1 = args[0]
        g_usdhcMmcOpt2 = args[1]
    elif group == uidef.kBootDevice_LpspiNor:
        global g_lpspiNorOpt0
        global g_lpspiNorOpt1
        g_lpspiNorOpt0 = args[0]
        g_lpspiNorOpt1 = args[1]
    else:
        pass

def getAdvancedSettings( group ):
    if group == uidef.kAdvancedSettings_Tool:
        global g_toolCommDict
        return g_toolCommDict
    elif group == uidef.kAdvancedSettings_Cert:
        global g_certSettingsDict
        return g_certSettingsDict
    elif group == uidef.kAdvancedSettings_OtpmkKey:
        global g_otpmkKeyOpt
        global g_otpmkEncryptedRegionStart
        global g_otpmkEncryptedRegionLength
        return g_otpmkKeyOpt, g_otpmkEncryptedRegionStart, g_otpmkEncryptedRegionLength
    elif group == uidef.kAdvancedSettings_UserKeys:
        global g_userKeyCtrlDict
        global g_userKeyCmdDict
        return g_userKeyCtrlDict, g_userKeyCmdDict
    else:
        pass

def setAdvancedSettings( group, *args ):
    if group == uidef.kAdvancedSettings_Tool:
        global g_toolCommDict
        g_toolCommDict = args[0]
    elif group == uidef.kAdvancedSettings_Cert:
        global g_certSettingsDict
        g_certSettingsDict = args[0]
    elif group == uidef.kAdvancedSettings_OtpmkKey:
        global g_otpmkKeyOpt
        global g_otpmkEncryptedRegionStart
        global g_otpmkEncryptedRegionLength
        g_otpmkKeyOpt = args[0]
        g_otpmkEncryptedRegionStart = args[1]
        g_otpmkEncryptedRegionLength = args[2]
    elif group == uidef.kAdvancedSettings_UserKeys:
        global g_userKeyCtrlDict
        global g_userKeyCmdDict
        g_userKeyCtrlDict = args[0]
        g_userKeyCmdDict = args[1]
    else:
        pass
