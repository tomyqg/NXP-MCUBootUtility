# nxpSecBoot

[![GitHub release](https://img.shields.io/github/release/JayHeng/nxp-sec-boot-ui.svg)](https://github.com/JayHeng/nxp-sec-boot-ui/releases/latest) [![GitHub commits](https://img.shields.io/github/commits-since/JayHeng/nxp-sec-boot-ui/v0.11.2.svg)](https://github.com/JayHeng/nxp-sec-boot-ui/compare/v0.11.2...master)

中文 | [English](./README-en.md)

### 1 软件概览
#### 1.1 介绍
　　nxpSecBoot是一个专为NXP MCU安全加密启动而设计的工具，其特性与NXP MCU里BootROM功能相对应，目前主要支持i.MXRT系列MCU芯片，与NXP官方提供的标准安全加密配套工具集（OpenSSL, CST, sdphost, blhost, elftosb, BD, MfgTool2）相比，nxpSecBoot是一个真正的一站式工具，一个工具包含NXP官方所有加密配套工具的功能，并且是全图形用户界面操作。借助于nxpSecBoot，你可以轻松上手NXP MCU安全加密启动。  
　　nxpSecBoot主要功能如下：  

> * 支持i.MXRT全系列MCU，包含i.MXRT1021、i.MXRT1051/1052、i.MXRT1061/1062、i.MXRT1064 SIP  
> * 支持UART和USB-HID两种串行下载方式（COM端口/USB设备自动识别）  
> * 支持五种常用格式(elf/axf/srec/hex/bin)源image文件输入  
> * 支持将源image文件自动转换成Bootable image  
> * 支持下载Bootable image进主动启动设备 - FlexSPI NOR、SEMC NAND接口Flash  
> * 支持下载Bootable image进备份启动设备 - LPSPI接口NOR/EEPROM Flash  
> * 支持DCD配置功能，可用于加载image进SDRAM执行  
> * 支持基于HAB实现的安全加密启动（单签名，签名和加密）  
> * 支持基于BEE实现的安全加密启动（唯一SNVS key，用户自定义key）  
> * 支持基于HAB和BEE联合实现的安全加密启动（HAB签名 & BEE加密）  
> * 支持MCU芯片内部eFuse的回读和烧写操作（即专用eFuse烧写器）  
> * 支持启动设备的任意读写擦操作（即通用Flash编程器）  
> * 支持从启动设备回读已下载的Bootable image数据，并对数据组成部分进行标注  

#### 1.2 下载
　　nxpSecBoot完全基于Python语言开发，并且源代码全部开源，其具体开发环境为Python 2.7.14、wxPython 4.0.3、pySerial 3.4、pywinusb 0.4.2、bincopy 15.0.0、PyInstaller 3.3.1。  

> * 安装包: https://github.com/JayHeng/nxp-sec-boot-ui/releases  
> * 源代码: https://github.com/JayHeng/nxp-sec-boot-ui  

　　nxpSecBoot在发布时借助PyInstaller将所有的Python依赖全部打包进一个可执行文件（\nxp-sec-boot-ui\bin\nxpSecBoot.exe），因此如果不是对nxpSecBoot的二次开发，你不需要安装任何Python软件及相关库。  

> Note: 源代码包里的nxpSecBoot.exe是在Windows 10 x64环境下打包的，也仅在该环境下测试过，如果因系统原因无法直接使用，你需要安装相应的Python开发环境，并在\nxp-sec-boot-ui\bin\目录下执行“pyinstaller .\nxpSecBoot.spec”命令重新生成nxpSecBoot.exe可执行文件。  

#### 1.3 安装
　　nxpSecBoot是一个是纯绿色免安装的工具，下载了源代码包之后，直接双击\nxp-sec-boot-ui\bin\nxpSecBoot.exe即可使用。使用nxpSecBoot没有任何软件依赖，不需要额外安装任何软件。  

> Note: nxpSecBoot安装包文件夹不能放置在含空格或中文的路径下，否则软件无法正常工作。  

#### 1.4 目录

　　nxpSecBoot软件目录组织如下：  
```text
\nxp-sec-boot-ui
                \apps                        --放置示例的源image文件
                \bin                         --放置nxpSecBoot可执行文件及PyInstaller打包描述文件
                \doc                         --放置NXP官方安全启动相关的参考文档
                \gen                         --放置nxpSecBoot使用过程中生成的临时文件
                      \bd_file                  --根据配置动态生成的BD文件
                      \bee_crypto               --BEE加密过程中生成的文件
                      \bootable_image           --生成的bootable image文件
                      \hab_cert                 --HAB签名过程中生成的文件
                      \hab_crypto               --HAB加密过程中生成的文件
                      \user_file                --软件运行过程中缓存的临时文件
                \gui                         --放置开发nxpSecBoot UI构建工程文件
                \img                         --放置nxpSecBoot使用过程中需加载的图片
                \src                         --放置开发nxpSecBoot的所有Python源代码文件
                \tools                       --放置nxpSecBoot使用过程中需调用的外部程序
                      \blhost                   --与Flashloader通信的上位机命令行工具
                      \cst                      --HAB加密的配套命令行工具
                      \elftosb                  --生成bootable image的命令行工具
                      \image_enc                --BEE加密的配套命令行工具
                      \openssl                  --生成证书和秘钥的标准工具
                      \sdphost                  --与ROM通信的上位机命令行工具
```

#### 1.5 界面
　　下图为nxpSecBoot工具的主界面，界面主要由六部分组成，各部分功能如下：  

![nxpSecBoot_mainWin_e](https://s1.ax1x.com/2018/12/07/F1j4Gn.png)

> * 【Menu Bar】：功能菜单栏，提供软件通用设置。  
> * 【Target Setup】：目标设备设置栏，提供MCU Device和Boot Device配置选项。  
> * 【Port Setup】：串行接口设置栏，选择用于连接MCU Device的接口。  
> * 【Device Status】：目标设备状态信息栏，当连接上目标设备之后，用于显示目标设备的状态。  
> * 【Main Window】：安全加密启动主界面，提供对目标设备做安全加密启动的所有操作。  
> * 【Log Window】：操作日志栏，记录软件操作日志。  

### 2 准备工作
　　在使用nxpSecBoot工具前主要有两个准备工作：一、准备好i.MXRT硬件板以及串行下载连接线（USB/UART）；二、准备好用于下载进Flash的源image文件。  
　　关于串行下载线连接，需要查看i.MXRT参考手册System Boot章节，确保连接的UART/USB引脚是BootROM指定的。  
　　关于源image文件准备，nxpSecBoot工具能够识别五种常见格式(elf/axf/srec/hex/bin)的image，唯一需要注意的是源image中不需要包含任何i.MXRT加载启动所需要的头（IVT, BootData等），nxpSecBoot会自动添加i.MXRT加载启动所需的文件头。  
　　以NXP官方SDK为例进一步讲解源image文件的生成，注册并登录NXP官网，来到 [MCUXpresso SDK Builder](https://mcuxpresso.nxp.com/en/select) 页面，选择合适的MCU芯片以及IDE（以RT1060芯片，IAR IDE为例）并点击Download SDK后便可得到SDK_2.4.0_EVK-MIMXRT1060.zip。  
　　使用IAR打开SDK包里的\boards\evkmimxrt1060\demo_apps\led_blinky\iar\led_blinky.eww示例应用：  

![nxpSecBoot_sdkProjectBuilds_e](https://s1.ax1x.com/2018/12/07/F1zSHO.png)

　　led_blinky应用其实包含了三个工程（ram/flexspi_nor/sdram），分别对应三个不同的linker文件（.icf），其中ram工程生成的image即是所谓的Non-XIP image，flexspi_nor工程生成的image即是所谓的XIP image。  
　　默认情况下，ram工程和flexspi_nor工程生成的image文件是无法直接为nxpSecBoot所用的，需要做一些小小的改变。  
　　ram工程需要修改linker文件如下：（推荐从0x3000开始链接中断向量表，中断向量表前面预留一段内存用于放置i.MXRT加载启动所需的文件头）。  

```text
define symbol m_interrupts_start       = 0x00003000;   // 0x00000000
define symbol m_interrupts_end         = 0x000033FF;   // 0x000003FF

define symbol m_text_start             = 0x00003400;   // 0x00000400
define symbol m_text_end               = 0x0001FFFF;

define symbol m_data_start             = 0x20000000;
define symbol m_data_end               = 0x2001FFFF;

define symbol m_data2_start            = 0x20200000;
define symbol m_data2_end              = 0x202BFFFF;
```

　　flexspi_nor工程需要修改工程配置选项里的Defined symbols如下：（将XIP_BOOT_HEADER_ENABLE设为0，即不需要生成包含i.MXRT加载启动文件头的image）。  

[![nxpSecBoot_sdkProjectOptions](https://s1.ax1x.com/2018/12/07/F3S9s0.png)](https://imgchr.com/i/F3S9s0)

　　如果只是为了快速验证nxpSecBoot工具，在nxpSecBoot\apps文件夹下默认存放了全系列恩智浦官方i.MXRT评估板的led_blinky应用的image文件。  

### 3 软件使用
#### 3.1 设置目标设备
　　在使用nxpSecBoot时首先需要配置目标设备，目标设备包括MCU Device和Boot Device。以NXP官方开发板EVK-MIMXRT1060为例，该开发板主芯片为i.MXRT1062DVL6A，所以【MCU Device】应设为i.MXRT106x。且以最常用的FlexSPI NOR启动为例，【Boot Device】设为FLEXSPI NOR，开发板上对应的外部存储芯片为IS25WP064AJBLE，其是一颗常用的四线QSPI NOR Flash，我们需要在软件里进一步配置该Boot Device，单击【Boot Device Configuration】按钮可弹出如下新的配置页面：  

![nxpSecBoot_flexspiNorCfgWin_e](https://s1.ax1x.com/2018/12/07/F1j52q.png)

　　在弹出的名为FlexSPI NOR Device Configuration页面里可以看到很多描述Multi-IO SPI NOR Flash特性的选项，比如Device Type、Query Pads等，这些选项都需要被正确地设置，以与开发板上的外部存储芯片相匹配。  
　　除此以外，页面上还有一个名为【Use Typical Device Model】的选项，nxpSecBoot软件预先定义了一些常用的Multi-IO SPI NOR Flash型号模型，如果开发板上的外部存储芯片恰好在软件预定义的型号列表里，那么你可以直接在【Use Typical Device Model】选择对应型号，而不必在Nor Option里逐一配置。  
　　EVK-MIMXRT1060开发板上的IS25WP064AJBLE芯片属于ISSI - IS25LP064A大类，因此我们只需要在【Use Typical Device Model】选择ISSI - IS25LP064A并点击【Ok】即完成了目标设备的设置。  

#### 3.2 连接目标设备
　　设置好目标设备之后，下一步便是连接目标设备，以USB-HID接口连接为例，给EVK-MIMXRT1060板子供电，并用USB Cable将PC与J9口连接起来，如果一切正常，应该可以在设备管理器找到vid,pid为0x1fc9,0x0135的HID-compliant vendor-defined device设备被枚举。如果没有发现该HID设备，请仔细检查板子SW7拨码开关是否将Boot Mode设为2'b01即Serial Downloader模式。  

![nxpSecBoot_usbhidDetected_e](https://s1.ax1x.com/2018/12/07/F1jhPs.png)

　　确认HID设备存在之后，在【Port Setup】选中USB-HID，然后直接点击【Connect to ROM】按钮，此时软件便会自动完成目标设备连接全过程（使用sdphost连接ROM，获取一些MCU内部寄存器信息，使用sdphost加载Flashloader并跳转过去，使用blhost连接Flashloader，获取一些eFuse信息，使用blhost去配置boot device并获取boot device meomry信息），这个过程需要大概5s的时间，如果目标设备连接正常，你可以看到指示灯变蓝，并且【Connect to ROM】按钮标签变为【Reset Device】。如果目标设备连接失败，指示灯会变红，并且【Connect to ROM】按钮标签变为【Reconnect】。  

![nxpSecBoot_connectedToDevice_e](https://s1.ax1x.com/2018/12/07/F1jIx0.png)

　　目标设备连接成功后可以在目标设备状态信息栏看到一些有用的设备状态信息，比如MCU芯片的UUID值、HAB状态、与启动相关的重要Fuse值，Boot Device的Page/Sector/Block大小等。  

#### 3.3 安全加密启动
　　目标设备连接成功后便可以开始最核心的安全加密启动操作，在做安全加密启动之前先来介绍安全加密启动主界面分布：  

![nxpSecBoot_secboot0_intro_e](https://s1.ax1x.com/2018/12/07/F1jTMV.png)

> * 【Image Generation Sequence】：image生成窗口，用于对源image进行加密安全处理，生成可放在Boot Device中的bootable image  
> * 【Image Loading Sequence】：image下载窗口，用于将生成的bootable image下载进Boot Device中，并且在MCU中烧录相应的Fuse值（各种Key，HAB设置等）  
> * 【eFuse Operation Utility】：eFuse回读与烧录窗口，用户可烧录自定义值进Fuse Region。  
> * 【Boot Device Memory】：image回读与标注显示窗口，用于从Boot Device回读已下载的Bootable image数据，并对数据组成各部分进行标注  
> * 【Secure Boot Type】：安全加密模式选择，选择想要安全模式（不使能安全，HAB单签名，HAB签名加密，BEE加密）。  
> * 【All-In-One Action】：一键操作，image生成窗口和image下载窗口里激活的操作自动按序执行  

##### 3.3.1 模式一：不启用任何安全措施
　　第一种模式是最简单的模式，即不启动任何安全措施，一般用于产品开发调试阶段。  
　　【Secure Boot Type】选择“Unsigned (XIP) Image Boot”，然后点击【Browse】按钮选择一个原始image文件（使用IDE生成的裸image文件即可，不需要包含任何i.MXRT启动所需的额外文件头），点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  

> Note: 软件如果设置为Auto-detect image format选项，则根据文件后缀名自动识别源文件格式。但是对于MCUXpresso或者GCC生成的axf文件，需要主动设置为".out(axf) from MCUXpresso/GCC ARM"。  

![nxpSecBoot_secboot1_unsigned](https://s1.ax1x.com/2018/12/07/F3A2ZR.png)

　　上图中Step4和Step5并不是必需操作，仅是用于确认【All-In-One Action】按钮操作是否成功，尤其是Step5操作，可以对应image下载窗口里显示的Bootable image构成图做一遍检查。  
　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，其余保持全0，重新上电便可以看到unsigned image正常执行了。  

##### 3.3.2 模式二：启用HAB签名认证
　　第二种模式是初级的安全模式，即仅对image进行签名认证，一般用于对产品安全性要求较高的场合。签名认证主要是对image合法性进行校验，检测image是否被异常破坏或篡改，如果检测发现image不合法，那么MCU便不会启动执行该image。  
　　【Secure Boot Type】选择“HAB Signed (XIP) Image Boot”，然后输入serial（必须是8位数字）以及key_pass（任意长度字符）后点击【Advanced Cert Settings】按钮配置所有签名认证的参数（熟悉 [NXP官方HAB Code Signing Tool工具](https://www.nxp.com/webapp/sps/download/license.jsp?colCode=IMX_CST_TOOL&appType=file2&location=null&DOWNLOAD_ID=null&lang_cd=en) 使用的朋友应该对这些设置很熟悉），再点击【Browse】按钮选择一个原始image文件，最后点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  

![nxpSecBoot_secboot2_signed](https://s1.ax1x.com/2018/12/07/F3A4JK.png)

　　上图中Step5主要确认两点：一、HAB状态是否是Closed的（Fuse 0x460[31:0]的bit1为1'b1）；二、SRKH是否被正确烧录（Fuse 0x580 - 0x5f0，一共256bit，即sha-256算法），SRKH是最终bootable image里CSF数据里的Public RSA Key的Hash值，用于校验Public RSA Key是否合法。  
　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，其余保持全0，重新上电便可以看到HAB signed image正常执行了。  
　　因为此时MCU芯片HAB状态已经是Closed，并且SRKH已经被烧录无法更改，所以未经签名认证的image无法正常运行，在软件目录\nxp-sec-boot\tools\cst\3.0.1\crts文件夹下存放着Private RSA Key文件，请妥善保存好，一旦遗失，那么新的image将无法被正确签名从而导致HAB认证失败无法被启动执行。  

##### 3.3.3 模式三：启用HAB签名认证与HAB加密
　　第三种模式是中级的安全模式，即对image进行签名认证以及HAB级加密，一般用于对产品安全性要求很高的场合。签名认证主要是对image合法性进行校验，而加密则可以保护image在外部Boot Device中不被非法盗用，因为在外部Boot Device中存放的是image的密文数据，即使被非法获取也无法轻易破解，并且加密是和MCU芯片绑定的，因为HAB加密过程中使用了MCU内部SNVS模块里的唯一Master Secret Key。  
　　【Secure Boot Type】选择“HAB Signed Encrypted Image Boot”，然后配置所有签名认证的参数（如果本地已有证书，可以不用配置，软件会尝试复用），再点击【Browse】按钮选择一个原始image文件，最后点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  

![nxpSecBoot_secboot3_hab_encrypted](https://s1.ax1x.com/2018/12/07/F3ARd1.png)

　　上图中Step6操作之后可以看到下载进Boot Deivce里的image部分确实是密文，实际上HAB加密仅支持加密image区域，其他区域（比如FDCB、IVT、Boot Data等）均没有加密。  
　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，其余保持全0，重新上电便可以看到HAB signed encrypted image正常执行了。  
　　你可能会好奇，既然image是经过HAB加密的，那么密码在哪里？怎么设置的？其实image加密操作完全被HAB配套工具封装好了，HAB加密使用的AES-128算法，其对应的128bits的AES-128 Key不是由用户自定义的，而是HAB加密工具自动随机生成的，并且每一次加密操作生成的AES-128 Key都是不一样的，即使你没有更换输入的原始image。AES-128 Key保存在\nxp-sec-boot\gen\hab_crypto\hab_dek.bin文件里。  
　　从上图中image下载窗口里显示的Bootable image构成图里可以看出，相比HAB单签名的方式，HAB签名加密方式最终使用的Bootable image的最后多了一个DEK KeyBlob组成部分，这个DEK KeyBlob是通过MCU芯片内部SNVS模块里的Master Secret Key对hab_dek.bin里的key数据进行动态加密生成的，因为Master Secret Key是芯片唯一的，因此DEK KeyBlob也是芯片唯一的，这是保护image不被非法盗用的关键。  
　　关于HAB加密为何不支持XIP Image，其实简单分析一下启动原理便清楚，Image在Boot Device里存储的是密文，这部分密文必须要经过HAB解密成明文才可以被CPU执行，因此必须要指定不同的存储空间去存放Image明文，Non-XIP image天然指定了明文应存放在芯片内部SRAM或者外挂SDRAM中，而XIP Image是在Boot Device中直接执行的，一般明文地址与密文地址是相同的，因此HAB加密不支持XIP Image。  

##### 3.3.4 模式四：启用单引擎BEE加密（唯一SNVS Key）
　　第四种模式是高级的安全模式，即用唯一SNVS Key对image进行单引擎BEE级加密，一般用于对产品安全性要求极高的场合。BEE加密与HAB加密的主要区别是执行解密操作的主体不同，主要有如下三点区别：  

> * HAB加密是由BootROM里的HAB将加密后的image全部解密成明文另存后再执行（静态解密），而BEE加密是由MCU芯片内部的BEE模块对加密后的image原地边解密边执行（动态解密）。  
> * HAB加密仅支持Non-XIP Image（不限Boot Device），而BEE加密仅支持XIP在FlexSPI NOR中的Image。  
> * HAB加密区域不可指定（默认全部用户Image区域），而BEE加密的区域可由用户指定。  

　　【Secure Boot Type】选择“BEE (Signed) Encrypted XIP Image Boot”，点击【Browse】按钮选择一个原始image文件（必须是XIP在FlexSPI NOR中的image），【Key Storage Region】选择“Fixed SNVS Key”后点击【Advanced Key Settings】按钮配置所有BEE加密的参数，最后点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  

![nxpSecBoot_secboot4_bee_encrypted_fixed_key](https://s1.ax1x.com/2018/12/07/F3AWIx.png)

　　上图中Step5操作主要确认一点：BEE_KEY0_SEL是否设置的是From OTPMK[255:128]（Fuse 0x460[31:0]的bit13,12为2'b10）。Step6操作之后可以看到下载进Boot Deivce里的Bootable image从IVT开始全是密文，本示例仅启用一块加密区域，具体对哪些区域进行加密是在【Advanced Key Settings】里指定的，最大支持指定3块加密区域。  
　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，并且将BT_CFG[1]设为1'b1（使能Encrypted XIP），其余保持全0，重新上电便可以看到BEE encrypted image正常执行了。  
　　BEE加密相比HAB加密是要更安全的，因为HAB加密毕竟是静态解密，当HAB解密完成之后在SRAM/SDRAM中存储的是全部的image明文，如果此刻黑客去非法访问SRAM/SDRAM是有可能获取全部image明文的；而BEE加密是动态解密，CPU执行到什么地方才会去解密什么地方，任何时候都不存在完整的image明文，黑客永远无法获取全部的image明文。  

##### 3.3.5 模式五：启用双引擎BEE加密（用户自定义Key）
　　第五种模式也是高级的安全模式，即用用户自定义Key对image进行双引擎BEE级加密，跟第四种模式（单引擎）原理类似，一般用于对产品安全性要求极高的场合。单引擎BEE加密与双引擎BEE加密具体区别如下：  

> * 唯一SNVS Key单引擎BEE加密默认使用SNVS Key，芯片出厂已预先烧录，无法更改；用户自定义Key双引擎BEE加密使用的Key是由用户自己设的，需要手动烧录在Fuse SW_GP2和GP4区域。  
> * 唯一SNVS Key单引擎BEE加密只启用了BEE引擎0；用户自定义Key双引擎BEE加密可以同时启用BEE引擎0和引擎1。但需要注意的是无论启动几个BEE引擎，最大加密区域总数均是3个。  

![nxpSecBoot_secboot5_bee_encrypted_flexible_key](https://s1.ax1x.com/2018/12/07/F3A5RO.png)

　　【Secure Boot Type】选择“BEE (Signed) Encrypted XIP Image Boot”，点击【Browse】按钮选择一个原始image文件（必须是XIP在FlexSPI NOR中的image），【Key Storage Region】选择“Flexible User Keys”后点击【Advanced Key Settings】按钮配置所有BEE加密的参数，最后点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  
　　有必要对如下使用Flexible User Keys加密的BEE参数设置页面再做一下介绍，首先是选择要激活的BEE引擎，可以单独激活BEE引擎0，也可以单独激活BEE引擎1，当然更可以同时激活BEE引擎0和1，本示例同时激活BEE引擎0和1。指定了BEE引擎后需要进一步为该引擎配置加密所使用的Key的存储空间以及需要用户手动输入Key（128bits）。最后还需要设置加密保护的区域，本示例共使能加密2个区域，分别为0x60001000 - 0x60001fff（由BEE引擎0保护），0x60002000 - 0x60002fff（由BEE引擎1保护）。  

![nxpSecBoot_flexibleUserKeysWin](https://s1.ax1x.com/2018/12/07/F3AcL9.png)

　　上图中Step5操作主要确认两点：一、BEE_KEY0_SEL是否设置正确（Fuse 0x460[31:0]的bit13,12）和BEE_KEY1_SEL是否设置正确（Fuse 0x460[31:0]的bit15,14）；二、用户Key是否被正确烧录（SW_GP2: Fuse 0x690 - 0x6c0，GP4: Fuse 0x8c0 - 0x8f0）。  
　　为了确认image是否按指定区域加密，你可以打开\nxp-sec-boot\gen\bootable_image\文件夹下面生成的未加密bootable image文件与image回读窗口里的内容进行比对。  
　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，并且将BT_CFG[1]设为1'b1（使能Encrypted XIP），其余保持全0，重新上电便可以看到BEE encrypted image正常执行了。  
　　双引擎BEE加密是将用户自定义的Key烧录进了Fuse SW_GP2/GP4区域里，但该区域的Fuse内容是可以回读的，如果黑客拿到Key，还是有可能破解存在外部Boot Device里的image密文，有没有对Fuse SW_GP2/GP4区域进行保护的方法？当然有，你可以对指定的Fuse区域进行加锁，可设置Fuse区域访问权限（读保护，写保护，覆盖保护），具体后面有单独章节详细介绍。  
　　双引擎BEE加密相比单引擎BEE加密，从破解角度来说难度加倍，毕竟可以启用两组不同的Key来共同保护image不被非法获取。  

##### 3.3.6 模式六：启用HAB签名认证与BEE加密
　　第六种模式是顶级的安全模式，即对image进行HAB签名认证以及BEE级加密（单引擎/双引擎均可），一般用于对产品安全性要求最高的场合。模式四以及模式五均只有加密功能，并没有对image进行合法性检测，引入HAB签名认证可以解决image合法性问题。  

　　【Secure Boot Type】选择“BEE (Signed) Encrypted XIP Image Boot”，【Enable Certificate For BEE Encryption】选择“Yes”并点击【Advanced Cert Settings】按钮配置所有签名认证的参数，点击【Browse】按钮选择一个原始image文件（必须是XIP在FlexSPI NOR中的image），【Key Storage Region】选择“Fixed SNVS Key”或者“Flexible User Keys”均可并点击【Advanced Key Settings】按钮配置所有BEE加密的参数，最后点击【All-In-One Action】按钮即可完成bootable image生成与下载所有操作。  

![nxpSecBoot_secboot6_signed_bee_encrypted](https://s1.ax1x.com/2018/12/07/F3Ahi6.png)

　　一切操作无误，板子上SW7拨码开关将Boot Mode设为2'b10即Internal Boot模式，并且将BT_CFG[1]设为1'b1（使能Encrypted XIP），其余保持全0，重新上电便可以看到BEE encrypted image正常执行了。  
　　需要特别注意的是，因为引入了HAB签名认证，如果BEE加密Key选择的是Fixed SNVS Key，需要在HAB Closed的状态下执行上述操作，否则会启动失败，这是HAB与BEE联合使用的限制。  

### 4 软件进阶
　　nxpSecBoot软件打开默认工作在Entry Mode下，可通过功能菜单栏Tools->Option选择进入Master Mode，在Master模式下开放了一些高级功能，适用于对NXP MCU芯片以及Boot ROM非常熟悉的用户。  

![nxpSecBoot_toolRunModeSet](https://s1.ax1x.com/2018/12/07/F3kxKJ.png)

#### 4.1 分步连接设备
　　进入Master模式下，可以不勾选One Step选项，这样可以单步去连接目标设备，单步连接的主要意义在于，可以在不配置Boot Device的情况下仅连接到Flashloader去实现eFuse操作。  

![nxpSecBoot_nonOneStepConnection](https://s1.ax1x.com/2018/12/07/F3Ewmd.png)

#### 4.2 专用eFuse烧写器
　　进入Master模式下，可以看到eFuse全部区域都开放了，你可以任意烧写指定的eFuse区域。eFuse操作是按bit一次性的（类似熔丝烧断），只能将0烧写成1，烧录成1之后便无法更改，所以eFuse的操作需要特别谨慎。  

![nxpSecBoot_fuseUnderMasterMode](https://s1.ax1x.com/2018/12/07/F3kzr9.png)

　　在上一章节安全加密启动过程中，我们会烧录SRKH(0x580 - 0x5f0)、SW_GP2(0x690 - 0x6c0)、GP4(0x8c0 - 0x8f0)，这些区域一经烧录便不得更改，甚至我们希望这些区域不仅不能被更改，也要不能被回读。  

![nxpSecBoot_fuseLockerBits](https://s1.ax1x.com/2018/12/07/F3EjB9.png)

　　从上图可知eFuse 0x400即是各Fuse功能区域的Locker，我们可以通过烧录eFuse 0x400来锁住SRKH, SW_GP2, GP4区域。那么如何烧录呢？其实非常简单，直接在各eFuse框内填写想要烧录的值，点击【Burn】按钮即可。  

#### 4.3 通用Flash编程器
　　进入Master模式下，可以点击【Read】、【Erase】、【Write】按钮实现已配置Flash的任意读擦写操作，这样可以将nxpSecBoot工具当做通用Flash编程器。  

![nxpSecBoot_flashProgrammer_e](https://s1.ax1x.com/2018/12/07/F3AdI0.png)
