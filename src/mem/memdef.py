import sys, os

kMemBlockOffset_EKIB0  = 0x400
kMemBlockOffset_EPRDB0 = 0x480
kMemBlockOffset_EKIB1  = 0x800
kMemBlockOffset_EPRDB1 = 0x880

kMemBlockSize_NFCB       = 0x400
kMemBlockSize_DBBT       = 0x420
kMemBlockSize_FDCB       = 0x200
kMemBlockSize_EKIB       = 0x20
kMemBlockSize_EPRDB      = 0x100
kMemBlockSize_IVT        = 0x20
kMemBlockSize_BootData   = 0x10
kMemBlockSize_CSF        = 0x1000
kMemBlockSize_KeyBlob    = 0x200

kMemberOffsetInIvt_Hdr      = 0x00
kMemberOffsetInIvt_Entry    = 0x04
kMemberOffsetInIvt_Dcd      = 0x0a
kMemberOffsetInIvt_BootData = 0x10
kMemberOffsetInIvt_Self     = 0x14
kMemberOffsetInIvt_Csf      = 0x18

