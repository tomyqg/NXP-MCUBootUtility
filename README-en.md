# nxpSecBoot

[![GitHub release](https://img.shields.io/github/release/JayHeng/nxp-sec-boot-ui.svg)](https://github.com/JayHeng/nxp-sec-boot-ui/releases/latest) [![GitHub commits](https://img.shields.io/github/commits-since/JayHeng/nxp-sec-boot-ui/v0.11.2.svg)](https://github.com/JayHeng/nxp-sec-boot-ui/compare/v0.11.2...master)

[中文](./README.md) | English

### 1 Overview
#### 1.1 Introduction
　　nxpSecBoot is a one-stop GUI tool to work with NXP MCU (Kinetis, i.MXRT, LPC) ROM bootloader, It can help you get started with security boot easily。  
　　Main features of nxpSecBoot：  

> * Support i.MXRT1021, i.MXRT1051/1052, i.MXRT1061/1062、i.MXRT1064 SIP  
> * Support both UART and USB-HID serial downloader modes  
> * Support five kinds of user bare image file format (elf/axf/srec/hex/bin)  
> * Support for converting bare image into bootable image  
> * Support FlexSPI NOR and SEMC NAND boot devices  
> * Support LPSPI NOR/EEPROM recovery boot device  
> * Support DCD which can help load image to SDRAM  
> * Support HAB encryption (Signed only, Signed and Encrypted)  
> * Support BEE encryption (SNVS Key, User Keys)  
> * Support HAB & BEE encryption (HAB Signed - BEE Encrypted)  
> * Support common eFuse memory operation (eFuse Programmer)  
> * Support common boot device memory operation (Flash Programmer)  
> * Support for reading back and marking bootable image from boot device  

