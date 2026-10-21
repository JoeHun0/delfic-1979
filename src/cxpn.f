      SUBROUTINE CXPN
C
C     H. G. NORMENT, ATMOSPHERIC SCIENCE ASSOCIATES - DECEMBER 1978
C
C     CXPN TABULATES THE CLOUD RISE AND EXPANSION OUTPUT TABLE ARRAY CX
C     AND TESTS FOR R-RATE, U,EK, AND MCX SHUT-OFF
C
C
      COMMON /BASIC/ W,FW,ZBRSTZ,HEIGHT,ZSCL,SLDTMP,TMSD,XGZ,YGZ,TGZ
      C MMON /CLOUD/ CHANGE,CMLR  ,C2    ,C3    ,C6    ,DEK    ,DRM    ,
     1 OS    ,DST   ,DST0  ,DST1  ,DST2  ,DT    ,DU    ,DWT    ,DX     ,
     2 0Z    ,ED    ,EK    ,EPS   ,ES    ,HLR   ,KS    ,KSV    ,MWYA   ,
     3 N     ,NNN   ,P     ,PW    ,R     ,RA    ,RL    ,RM     ,RZT    ,
     4 S     ,SAVE  ,SHAPE ,SMALLT,T     ,TE    ,U     ,V      ,WT     ,
     5 X     ,XE    ,Z     ,ZBFR  ,ZLMT  ,SPARE
      COMMON /CONTRL/ DETID(12),IC(20),IRAD,IRISE,ISIN,ISOUT,JPARN,KOI
      COMMON /INITL/ F, PHI, SSAM, TME, TMPG, TMPS, VPR
      COMMON /TABLES/ MCX, CX(50,10), GOPST(10,100)
C
      DATA WORD1, WORD2, WCRD3 /6HR RATE, 6H MCX  : 6H U,EK /
C
 5000 FORMAT(//////10X,46HCLOU DRIS EI STERMINATE DI NCXP NA TSTATEMEN T
     14, 8H BY THE A6, 7H SWITCH///)
C
C  ← 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 2
C
C     PERFORM FIRST PASS INITIALIZATION
C
      GO TO (002, 020, 040), MWYA
  002 DO 004 MJ = 1, 10
      DO 004 MI = 1, 50
  004 CX (MI, MJ) = 0.0
      MCX = 1
      MWYA = 2
      DLTM = 3.0
      TSTM = SMALLT
      TSRE = AMAX1(10., AMIN1( 23. + 9. * ALOG10( W ), 60. ))
      TSRD=EXP(0.014778*ALOG(W)-7.0499)
      ZBFR = Z
      GO TO 040
C
C     IS IT TIME TO RECORD CLOUD STATUS IN THE CX ARRAY
C YES = TO 1.40
C        No - 70 37C
C
  020 IF ( SMALLT - TSTM ) 070, 040, 040
  040 CX (MCX, 1) = SMALLT
      IF (Z - ZBFR) 041, 042, 042
  041 ZA = ZBFR
      GO TO 043
  642 7A = 7
  043 CX (MCX, 5) = R
      CX (MCX, 9) = T
      CX(MCX,10)=RA
C TEST TO NO CR+ COMPUTATION
      TF: MCK .LE. 5 ) GO TO 543
      TSTR = ABS(CX(MCX,5) - CX(MCX-1,5)) /
     1       ((CX(MCX,1) - CX(MCX-1,1)) * CX(MCX,5))
      IF( TSRD .LT. TSTR  .OR.  U .GT. 0.0 ) GC TO 343
  243 MHYA = 3
      NSTAT=243
      WRITE(ISOUT,5000)NSTAT,WORD1
      GO TO 543
  343 IF( TSRE .LT. EK  .CR.  U .GT. 0.0 ) GO TO 543
  443 MWYA = 3
      NSTAT=443
      WRITE(ISOUT,5000)NSTAT,WORD3
  543 CX (MCX, 3) = ZA - RZT
      CX (MCX, 4) = ZA + RZT
  060 MCX = MCX + 1
C                                         CHECK CAPACITY OF ARRAY CX
      IF (MCX - 50) 062, 062, 061
  061 MWYA = 3
      NSTAT=61
      WRITE(ISOUT,5000)NSTAT,WORD2
  C62 CXM = MCX
C
C     COMPUTE THE TIME AT WHICH THE NEXT CX ARRAY ENTRIES ARE TO BE MADE
C
      DLTM = DLTM + CXM * .084946
      TSTM = TSTM + DLTM
  065 IF (Z - Z8FR) 068, 068, 067
  067 ZBFR = Z
  068 GO TO (070, 070, 100), MHYA
  070 RETURN
C                                         COMPLETE OUTPUT CX TABLE
  100 MCX = MCX - 1
      IF (CX (MCX - 1, 1) - CX (MCX, 1)) 102, 100, 102
  102 00 104 MK = 2, MCX
C                                         COMPUTE TIME INTERVAL LENGTH
      CX (MK - 1, 2) = CX (MK, 1) - CX (MK - 1, 1)
C                                         COMPUTE VERTICAL RATES
      CX (MK - 1, 6) = (CX (MK, 3) - CX (MK - 1, 3)) / CX (MK - 1, 2)
      CX (MK-1, 7) = (CX (MK, 4) - CX(MK-1, 4)) / CX (MK-1, 2)
C                                         COMPUTE RADIAL RATE
  104 CX (MK - 1, 8) = (CX (MK, 5) - CX (MK - 1, 5)) / CX (MK - 1, 2)
      DO 106 ML = 1, MCX
  106 CX (ML, 1) = CX (ML, 1) + TME
      GO TO 070
      END
