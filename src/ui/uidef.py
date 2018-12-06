import wx
import sys, os

kConnectStage_Rom            = 1
kConnectStage_Flashloader    = 2
kConnectStage_ExternalMemory = 3
kConnectStage_Reset          = 4

kConnectStep_Fast   = 3
kConnectStep_Normal = 1

kBootSeqColor_Invalid  = wx.Colour( 160, 160, 160 )
kBootSeqColor_Optional = wx.Colour( 166, 255, 255 )
kBootSeqColor_Active   = wx.Colour( 147, 255, 174 )

kMcuSeries_iMXRT   = 'i.MXRT'
kMcuSeries_LPC     = 'LPC'
kMcuSeries_Kinetis = 'Kinetis'

kMcuSeries_v0_11_x = [kMcuSeries_iMXRT]

kMcuDevice_iMXRT102x = 'i.MXRT102x'
kMcuDevice_iMXRT105x = 'i.MXRT105x'
kMcuDevice_iMXRT106x = 'i.MXRT106x'
kMcuDevice_iMXRT1064 = 'i.MXRT1064 SIP'

kBootDevice_FlexspiNor     = 'FLEXSPI NOR'
kBootDevice_FlexspiNand    = 'FLEXSPI NAND'
kBootDevice_SemcNor        = 'SEMC NOR'
kBootDevice_SemcNand       = 'SEMC NAND'
kBootDevice_UsdhcSd        = 'uSDHC SD'
kBootDevice_UsdhcMmc       = 'uSDHC MMC/eMMC'
kBootDevice_LpspiNor       = 'LPSPI NOR/EEPROM'
kBootDevice_RamFlashloader = 'RAM FLASHLOADER'

kBootDevice_v0_11_x = [kBootDevice_FlexspiNor, kBootDevice_SemcNand, kBootDevice_LpspiNor]

kSecureBootType_Development = 'Unsigned (XIP) Image Boot'
kSecureBootType_HabAuth     = 'HAB Signed (XIP) Image Boot'
kSecureBootType_HabCrypto   = 'HAB Signed Encrypted Image Boot'
kSecureBootType_BeeCrypto   = 'BEE (Signed) Encrypted XIP Image Boot'

kKeyStorageRegion_FixedOtpmkKey    = 'Fixed SNVS Key'
kKeyStorageRegion_FlexibleUserKeys = 'Flexible User Keys'

kAdvancedSettings_Cert      = 1
kAdvancedSettings_BD        = 2
kAdvancedSettings_OtpmkKey  = 3
kAdvancedSettings_UserKeys  = 4

kCstVersion_Invalid = 'x.x.x'
kCstVersion_v2_3_3  = '2.3.3'
kCstVersion_v3_0_1  = '3.0.1'
kCstVersion_v3_1_0  = '3.1.0'

kCstVersion_Avail   = [kCstVersion_v3_0_1]

kPkiTreeKeySel_IsEcc  = ['p256', 'p384', 'p521']
kPkiTreeKeySel_NotEcc = ['1024', '2048', '3072', '4096']

kUserEngineSel_Engine0     = 'Engine 0'
kUserEngineSel_Engine1     = 'Engine 1'
kUserEngineSel_BothEngines = 'Both Engines'

kSupportedEngineSel_iMXRT102x = [kUserEngineSel_Engine0, kUserEngineSel_Engine1]
kSupportedEngineSel_iMXRT105x = [kUserEngineSel_Engine0, kUserEngineSel_Engine1]
kSupportedEngineSel_iMXRT106x = [kUserEngineSel_Engine0, kUserEngineSel_Engine1, kUserEngineSel_BothEngines]
kSupportedEngineSel_iMXRT1064 = [kUserEngineSel_Engine0, kUserEngineSel_Engine1, kUserEngineSel_BothEngines]

kUserKeySource_OTPMK  = 'Fuse OTPMK[255:128]'
kUserKeySource_SW_GP2 = 'Fuse SW-GP2'
kUserKeySource_GP4    = 'Fuse GP4[127:0]'

kSupportedKeySource_iMXRT102x = [kUserKeySource_SW_GP2]
kSupportedKeySource_iMXRT105x = [kUserKeySource_SW_GP2]
kSupportedKeySource_iMXRT106x = [kUserKeySource_SW_GP2, kUserKeySource_GP4]
kSupportedKeySource_iMXRT1064 = [kUserKeySource_SW_GP2, kUserKeySource_GP4]

kMaxFacRegionCount = 3

kMemBlockColor_Background = wx.WHITE
kMemBlockColor_Padding    = wx.BLACK
#kMemBlockColor_FCB        = wx.
#kMemBlockColor_DBBT       = wx.
kMemBlockColor_CFG        = wx.Colour( 0x00, 0xff, 0xff ) #wx.CYAN
kMemBlockColor_EKIB       = wx.Colour( 0xb0, 0x00, 0xff ) #wx.PURPLE
kMemBlockColor_EPRDB      = wx.Colour( 0xa5, 0x2a, 0x2a ) #wx.BROWN
kMemBlockColor_IVT        = wx.RED
kMemBlockColor_BootData   = wx.GREEN
kMemBlockColor_DCD        = wx.Colour( 0x6f, 0x42, 0x42 ) #wx.SALMON
kMemBlockColor_Image      = wx.BLUE
kMemBlockColor_CSF        = wx.Colour( 0xff, 0xc0, 0xcb ) #wx.PINK
kMemBlockColor_KeyBlob    = wx.Colour( 0xff, 0x7f, 0x00 ) #wx.CORAL

kSecureBootSeqStep_AllInOne   = 0
kSecureBootSeqStep_GenCert    = 1
kSecureBootSeqStep_GenImage   = 2
kSecureBootSeqStep_PrepBee    = 3
kSecureBootSeqStep_ProgSrk    = 4
kSecureBootSeqStep_OperBee    = 5
kSecureBootSeqStep_FlashImage = 6
kSecureBootSeqStep_ProgDek    = 7
