      SUBROUTINE CPFR
C
C     H. G. NORMENT, ATMOSPHERIC SCIENCE ASSOCIATES - DECEMBER 1978
C
C
C     CPFR COMPUTES PARTICLE FALLOUT RATE
C
C
      COMMON /CLOUD/ CHANGE,CMLR  ,C2    ,C3    ,C6    ,DEK    ,DRM    ,
     1 DS    ,OST   ,OST0  ,OST1  ,OST2  ,UT    ,DU    ,DWT    ,DX     ,
     2 DZ    ,ED    ,EK    ,EPS   ,ES    ,HLK   ,KS    ,KSV    ,MWYA   ,
     3 N     ,NNN   ,P     ,PW    ,R     ,RA    ,RL    ,RM     ,RZT    ,
     4 S     ,SAVE  ,SHAPE ,SMALLT,T     ,TE    ,U     ,V      ,WT     ,
     5 X     ,XE    ,Z     ,ZBFR  ,ZLMT  ,SPARE
      COMMON /CONTRL/ DETIO(12),IC(20),IRAD,IRISE,ISIN,ISOUT,JPARN,KDI
      COMMON /PARTCL/ NDSTR,RHOP,DMEAN,SD,PS(200),DIAM(201),FMASS(200)
      COMMON /TABLES/ MCX, CX(50,10), GDPST(1J,100)
C
      DIMENSION Y(200),CG(200)
      EQUIVALENCE (Y(1),GOPST(1)), (CG(1),GOPST(201))
C
  903 FORMAT (1H1/////////)
     1  20X30HNEGATIVE PARTICLE DENSITY                          /////)
  758 FORMAT(1H124X73H* * * * * * * * * * * * * * * * * * * * * * * * *
     1* * * * * * * * * * * *//  22X, 76HPARTICLE SETTLING RATES ARE INA
     2CCURATE.  DAVIES NUMEER IS TOO LARGE FOR THE I3, 8H TH SIZE// 24X,
     3 73H* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
     4* * * * * *///)
C
C
C                                      TEST FOR IMPOSSIBLE PARTICLE
      DO 901 J=1,NDSTR
      IF(Y(J)) 902, 901, 901
9:1        1CONTINU
           GO TO 9.
  902 WRITE(ISOUT,903)
      MWYA = 3
      GO TO 008
900        CONTINUE
C
C     COMPUTE PARTICLE FALLOUT RATES
C
      VIS=1.458E-6*T**1.5/(110.4+T)
      DO 3 J=1,NDSTR
      CALL SETTLE(PS(J), R+OF, RA, VIS, T, P, CG(J), IACCR)
      IF(MWYA.EQ. 1  .ANC.  IACCR .NE. 0) WRITE(ISCUT,758) J
   3  CONTINUE
C
C     COMPUTE OVERALL LOSS RATE OF FALLOUT FROM THE CLOUD AND ADJUST
C     IN-CLOUD PARTICLE CONCENTRATIONS
C
      CMLR=0.
      A=3.1415927*K**2*DST
      DO 1 J=1,NDSTR
      C=0.5235988*PS(J)**3
      D=A*CG(J)
      CHLR=CHLR+C*D*Y(J)
    1 Y(J)=Y(J)*(1.-0/V)
      CMLR=CMLR*RHOP/DST
  008 RETURN
      END
