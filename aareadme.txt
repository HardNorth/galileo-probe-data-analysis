PDS_VERSION_ID        = PDS3                                                  
                                                                              
RECORD_TYPE           = FIXED_LENGTH                                          
RECORD_BYTES          = 80                                                    
OBJECT                = TEXT                                                  
  INTERCHANGE_FORMAT    = ASCII                                               
  PUBLICATION_DATE      = 2002-01-15                                          
  NOTE                  = "N/A"                                               
END_OBJECT            = TEXT                                                  
                                                                              
END                                                                           
                                                                              
                             Volume GP_0001                                   
                     Galileo Probe Data Set Archive                           
                                                                              
                                                                              
                            AAREADME.TXT                                      
                           15 January 2002                                    
                            Lyle F. Huber                                     
                     New Mexico State University                              
                                                                              
                                                                              
=================================================================             
INTRODUCTION                                                                  
=================================================================             
                                                                              
     This compact disc contains archival data produced from the Galileo       
Entry Probe mission to Jupiter.                                               
                                                                              
                                                                              
=================================================================             
VOLUME INFORMATION                                                            
=================================================================             
                                                                              
     This disc contains eight data sets as described below. The data sets are:
                                                                              
(1) ASI - This data set contains data from the Atmospheric Structure          
Instrument.                                                                   
                                                                              
(2) DWE - This data set contains data from the Doppler Wind Experiment,       
which is not an actual instrument on board the Probe but an analysis of the   
radio signals to determine the atmospheric winds.                             
                                                                              
(3) EPI - This data set contains data from the Energetic Particle Instrument. 
                                                                              
(4) HAD - This data set contains data from the Helium Abundance Detector.     
                                                                              
(5) LRD - This data set contains data from the Lightning and Radio Emission   
Detector.                                                                     
                                                                              
(6) NEP - This data set contains data from the Nephelometer.                  
                                                                              
(7) NFR - This data set contains data from the Net Flux Radiometer.           
                                                                              
(8) NMS - This data set contains data from the Neutral Mass Spectrometer.     
                                                                              
    This volume follows the structure outlined below:                         
                                                                              
           root                                                               
            |                                                                 
            |- AAREADME.TXT          The file you are reading.                
            |                                                                 
            |- ERRATA.TXT            Description of known anomalies and       
            |                        errors present on this volume.           
            |                                                                 
            |- VOLDESC.CAT           A description of the contents of this    
            |                        CD_ROM volume in a format readable by    
            |                        both humans and computers.               
            |                                                                 
            |- [CATALOG]             A directory containing information       
            |     |                  about the Galileo Probe data sets        
            |     |                                                           
            |     |- CATINFO.TXT     Description of files in this directory.  
            |     |                                                           
            |     |- MISSION.CAT     Description of the Galileo Probe         
            |     |                  mission.                                 
            |     |                                                           
            |     |- GPHOST.CAT      Description of the Galileo Probe         
            |     |                  spacecraft.                              
            |     |                                                           
            |     |- *INST.CAT       Description of the Probe instruments.    
            |     |                                                           
            |     |- *DS.CAT         Descriptions of the data sets.           
            |     |                                                           
            |     |- PERS.CAT        A listing of the people involved in the  
            |     |                  production of these data sets and        
            |     |                  this CD-ROM.                             
            |     |                                                           
            |     |- REF.CAT        A list of pertinent references.           
            |                                                                 
            |- [DOCUMENT]            A directory containing other supporting  
            |                        documentation.                           
            |                                                                 
            |- [INDEX]               A directory containing an index of data  
            |                        files on this disk.                      
            |                                                                 
            |- [SOFTWARE]            A directory containing supporting        
            |                        software.                                
            |                                                                 
            |- [DATA]                A directory containing the data files    
                  |                  and PDS labels describing the contents   
                  |                  of those files.                          
                  |                                                           
                  |- [ASI]                                                    
                  |                                                           
                  |- [DWE]                                                    
                  |                                                           
                  |- [EPI]                                                    
                  |                                                           
                  |- [HAD]                                                    
                  |                                                           
                  |- [LRD]                                                    
                  |                                                           
                  |- [NEP]                                                    
                  |                                                           
                  |- [NFR]                                                    
                  |                                                           
                  |- [NMS]                                                    
                                                                              
                                                                              
=================================================================             
DISC FORMAT                                                                   
=================================================================             
                                                                              
    This disk has been formatted so that a variety of computer systems        
(e.g. IBM PC, Macintosh, Sun, VAX) may access the data.  Specifically,        
the disk is formatted according to the ISO 9660 level 1 Interchange           
Standard.  For further information, refer to the ISO 9660 Standard            
Document: RF# ISO 9660-1988, 15 April 1988.                                   
                                                                              
                                                                              
=================================================================             
FILE FORMAT                                                                   
=================================================================             
                                                                              
     Most data files on this disc are accompanied by detached                 
PDS labels, which describe their contents.  Some data files and PDS TEXT      
objects include attached labels. Labels have the same file name as the        
primary data file but have a suffix ".LBL" appended.                          
The HAD data file and most of the NFR data files have attached labels.        
                                                                              
                                                                              
=================================================================             
PEER REVIEW                                                                   
=================================================================             
                                                                              
    This volume is undergoing a peer review by the PDS. The peer review       
panel will consist of Lyle Huber, Steve Joy and Tyler Brown representing PDS, 
members of instrument teams and external reviewers.                           
                                                                              
=================================================================             
CITATION INFORMATION                                                          
=================================================================             
                                                                              
    Users wishing to cite this volume in publications should adopt the        
following as the method of citation:                                          
                                                                              
   ASI:   A. Seiff, T.C.D. Knight,                                            
          R.F. Beebe and L.F. Huber, GP-J-ASI-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   DWE:   D.H. Atkinson, J.B. Pollack, A. Seiff,                              
          R.F. Beebe and L.F. Huber, GP-J-DWE-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   EPI:   H.M. Fischer, J.D. Mihalov, E. Pehlke,                              
          R.F. Beebe and L.F. Huber, GP-J-EPI-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   HAD:   U. Von Zahn, D.M. Hunten,                                           
          R.F. Beebe and L.F. Huber, GP-J-HAD-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   LRD:   K. Rinnert, L.J. Lanzerotti,                                        
          R.F. Beebe and L.F. Huber, GP-J-LRD-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   NEP:   B. Ragent, D.S. Colburn, K.A. Rages,                                
          R.F. Beebe and L.F. Huber, GP-J-NEP-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   NFR:   L.A. Sromovsky, P.M. Fry, A.D. Collard,                             
          R.F. Beebe and L.F. Huber, GP-J-NFR-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
   NMS:   H.B. Niemann, J.A. Haberman, W.T. Kasprzak,                         
          R.F. Beebe and L.F. Huber, GP-J-NMS-3-ENTRY-V1.0, NASA Planetary    
          Data System, 2000.                                                  
                                                                              
=================================================================             
DISCLAIMER                                                                    
=================================================================             
                                                                              
     Although considerable care has gone into making this volume              
set, errors are both possible and likely.  Users of the data are              
advised to exercise the same caution as they would when dealing with          
any other unknown data set.                                                   
                                                                              
     Reports of errors or difficulties would be appreciated.  Please          
contact the person listed below or the PDS Operator.                          
                                                                              
                                                                              
=================================================================             
WHOM TO CONTACT FOR INFORMATION                                               
=================================================================             
                                                                              
For questions concerning this volume or the data sets and documentation       
contained herein, contact:                                                    
                                                                              
Lyle F. Huber                                                                 
Department of Astronomy                                                       
New Mexico State University                                                   
P.O. Box 30001, MSC 4500                                                      
Las Cruces, NM  88003-0001                                                    
Phone: 505-646-1862                                                           
Email: lhuber@nmsu.edu                                                        
                                                                              
