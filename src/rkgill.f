      SUBROUTINE RKGILL
C
C     H. G. NORMENT, ATMOSPHERIC SCIENCE ASSOCIATES - DECEMBER 1978
C
C
C       INTEGRATES THE CLOUD RISE DIFFERENTIAL EQUATIONS VIA THE
C       RUNGE-KUTTA-GILL METHOD
C
C
       COMMON /ATMOS/ NAT, ALT(256),  ATP(256),  PHS(256), KLH(256),
     1        RHO(256), ETA(25€), NHODO, ZV(100),  VX(100), VY(100)
      COMMON /CLOUD/ CHANGE,CMLR  ,C2    ,C3    ,C6    ,DEK    ,DRM    ,
     1 OS    ,OST   ,OST0  ,OST1  ,OST2  ,OT    ,DU    ,DWT    ,DX     ,
     2 DZ    ,ED    ,EK    ,EPS   ,ES    ,HLR   ,KS    ,KSV    ,MWYA   ,
     3 N     ,NNN   ,P     ,PW    ,R     ,KA    ,RL    ,RM     ,RZT    ,
     4 S     ,SAVE  ,SHAPE ,SMALLT,T     ,TE    ,U     ,V      ,WT     ,
     5 X     ,XE    ,Z     ,ZBFR  ,ZLMT  ,SPARE
C
      DIMENSION DVBL(8),VEL(8),RKG(8)
C
C
      H=DST
      KS  =0
      KYCL=1
C
      V8L(1)=WT
      VBL(2)=RM
      VBL(3)=U
      V9L(4)=X
      VBL(5)=T
      VBL(6)=Z
      V8L(7)=EK
      VBL(8)=S
C
   20 CALL DERIV
      IF(ABS(U).LT. 1.E-10) VBL(3)=0.
      DV3L(1)=DWT
      DV3L(2)=DRM
      DV8L（3）=OU
      OVBL(4)=DX
      DV8L(5)=DT
      DV9L(6)=DZ
      DV3L(7)=DEK
      DVBL(8)=DS
C
      KS=KS+1
      GO TO (1,3,5,7),KS
C
    1 00 2 J=1,8
      VBL(J)=VBL(J)+0.5*H*DVBL(J)
    2 RKG(J)=DVBL(J)
      GO TO 10
    3 00 4 J=1,8
      VBL(J)=VBL(J)+.29289322*H*(DVBL(J)-RKG(J))
    4 RKG(J)=.58578644*DVBL(J)+.12132034*RKG(J)
      GO TO 10
    5 00 6 J=1,8
      VBL(J)=VBL(J)+1.7071068*H*(DVBL(J)-RKG(J))
    6 RKG(J)=3.41421356*DVBL(J)-4.1213203*RKG(J)
      GO TO 10
    7 00 8 J=1,8
    8 VBL(J)=VBL(J)+.16666667*H*(DVBL(J)-2.*RKG(J))
C
      KYCL=2
   10 HT=VBL(1)
      RM=VBL(2)
      U=VBL(3)
      X=VBL(4)
      T=V9L(5)
      Z=VBL(6)
      EK=VBL(7)
      S=VBL(8)
      CALL TRPL(Z,NAT ,ALT,PRS,PQR)
      V=287.*T*RM*(1.+X)/PQR/(1.+X+S+WT)*(1.0+X*29./18.)/(1.0+X)
      IF( U .GT. 0.0 ) RZT = ( 0.2387324 * V * SHAPE**2 )**0.3333333333
      GO TO(20,30),KYCL
   30 RETURN
      END
