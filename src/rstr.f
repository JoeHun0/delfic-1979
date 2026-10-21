      SUBROUTINE RSTR
C
C     H. G. NORMENT, ATMOSPHERIC SCIENCE ASSOCIATES - DECEMBER 1978
C
C
C     RSTR PRESERVES AND/OR RESTORES CRM VARIABLES
C
C
      COMMON /CLOUD/ CHANGE,CMLR  ,C2    ,C3    ,C6    ,DEK    ,DRM    ,
     1 DS    ,DST   ,DST0  ,DST1  ,DST2  ,DT    ,DU    ,CWT    ,DX     ,
     2 DZ    ,ED    ,EK    ,EPS   ,ES    ,HLR   ,KS    ,KSV    ,MWYA   ,
     3 N     ,NNN   ,P     ,PW    ,R     ,RA    ,RL    ,KM     ,RZT    ,
     4 S     ,SAVE  ,SHAPE ,SMALLT,T     ,TE    ,U     ,V      ,WT     ,
     5 X     ,XE    ,Z     ,ZBFR  ,ZLMT  ,SPARE
      COMMON /PARTCL/ NDSTR,RHOP,DMEAN,SD,PS(260),UIAM(201),FMASS(203)
      COMMON /TABLES/ MCX, CX(50,10), GDPST(1J,1J0)
C
      DIMENSION PY(200), Y(200)
      EQUIVALENCE (Y(1),GOPST(1)), (PY(1),GOPST(401))
C
C
      GO TO(1,3),KSV
    1 PEK=EK
      PRM=RM
      PSS=S
      PT=T
      PU=U
      PV=V
      PWT=WT
      PX=X
      PZ=Z
      PRZT=RZT
      00 2 NP=1,NDSTR
    2 PY(NP)=Y(NP)
      GO TO 5
C
    3 SMALLT=SMALLT-DST
      DST = DST1
      EK=PEK
      RM=PRM
      S=PSS
      T=PT
      U=PU
      V=PV
      WT=PWT
      X=PX
      Z=PZ
      RZT=PRZT
      DO 4 NP=1,NDSYR
    4 Y(NP)=PY(NP)
      N=3
    5 RETURN
      END
