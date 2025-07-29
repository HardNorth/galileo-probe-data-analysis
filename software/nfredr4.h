/*
**	nfredr4.h
**
**	Include file for program to read Galileo NFR EDR files.
**
*/

#define True 1
#define False 0

#define RECMAX 206

#define NF 0
#define UF 1
#define AZ 2
#define BC 3

/*	Time offsets for converting DC, IC to time after minor frame
**	zero.
**
**	Time after MF0, in seconds, is
**
**	T = DC * 120 + IC * 6 + OFF,
**
**	where OFF is IC_MID_OFF for NF, UF, and BC
**	             SC_MID_OFF for AZ, and SC
**	             HK_OFF for all housekeeping data
*/

#define IC_MID_OFF 6.75
#define SC_MID_OFF 8.25
#define HK_OFF     9.75

typedef struct {
	int data_valid;
	unsigned long mfnum;
	unsigned char nfrmfw[8];
	unsigned char mfw52;
} MF;

typedef struct {
	int data_valid;
	unsigned char data_wds[12];
	int sub_id;
	unsigned char sub_data;
} ICRaw;

typedef struct {
	unsigned long start_mf;
	ICRaw ic[20];
} DCRaw;

typedef struct {
	int data_valid;
	int error;
	int mode;
	long chan_data[6];
	float hk_data[2];
	int sub_id;
	float sub_data;
} ICEng;

typedef struct {
	unsigned long start_mf;
	ICEng ic[20];
	long gsa_data[6];
	int rdt_data[5];
	float dt_data[5];
} DCEng;

static char *mode_name[4] = {
	"NF", "UF", "AZ", "BC"
};

#define HB 0
#define A1 1
#define A2 2
#define WT 3
#define DT 4
#define ET 5
#define V1 6
#define V2 7
#define SW 8
#define BI 9
#define WI 10

static int hk_order[20][2] = {
	HB, A1, A2, WT, V2, A2, A1, A2, ET, WT,
	SW, SW, V1, WT, A1, A2, HB, WT, HB, WT,
	HB, WT, A1, A2, V2, A1, A2, WT, ET, WT,
	A1, A2, V1, WT, A1, A2, HB, WT, HB, A2
};

static char *hk_name[20][2] = {
	"HB", "A1", "A2", "WT", "V2", "A2", "A1", "A2", "ET", "WT",
	"SW", "SW", "V1", "WT", "A1", "A2", "HB", "WT", "HB", "WT",
	"HB", "WT", "A1", "A2", "V2", "A1", "A2", "WT", "ET", "WT",
	"A1", "A2", "V1", "WT", "A1", "A2", "HB", "WT", "HB", "A2"
};

static char *hk_fmt[20][2] = {
	" %5.1f ", " %5.1f", " %5.1f ", " %5.1f", "  %5.2f", " %5.1f",
	" %5.1f ", " %5.1f", " %5.1f ", " %5.1f", " %3.0f   ", " %3.0f  ",
	"  %5.2f", " %5.1f", " %5.1f ", " %5.1f", " %5.1f ", " %5.1f",
	" %5.1f ", " %5.1f", " %5.1f ", " %5.1f", " %5.1f ", " %5.1f",
	"  %5.2f", " %5.1f", " %5.1f ", " %5.1f", " %5.1f ", " %5.1f",
	" %5.1f ", " %5.1f", "  %5.2f", " %5.1f", " %5.1f ", " %5.1f",
	" %5.1f ", " %5.1f", " %5.1f ", " %5.1f"
};

static float vtherm = 0.50213;

/* hk_parms order: HB, A1, A2, WT, DT, ET, V1, V2, SW, BI, WI */
static double hk_parms[11][5] = {
	9.65154E-4, 2.56476E-4, 1.18276E-7, 8440.60, 523.0,
	1.01832E-3, 2.57467E-4, 1.16199E-7, 98700.0, 1.0E4,
	1.02032E-3, 2.57335E-4, 1.13081E-7, 4.0E6, 2.0E5,
	9.68640E-4, 2.58757E-4, 1.29717E-7, 98700.0, 1.0E4,
	-1.90100E+01, 3.48621E-01, 0.0, 0.0, 0.0,
	-2.36471E+01, 3.53496E-01, 0.0, 0.0, 0.0,
	0.0, 0.0617709, 0.0, 0.0, 0.0,
	0.0, 0.0316181, 0.0, 0.0, 0.0,
	0.0, 1.0, 0.0, 0.0, 0.0,
	0.0, 7.89000E-01, 0.0, 0.0, 0.0,
	0.0, 1.09700E-01, 0.0, 0.0, 0.0
};

#define NUMF 23
#define AZF 0
#define UFF 1
#define BCF 2
#define SCF 3
#define NFF 4
#define HBF 5
#define A1F 6
#define A2F 7
#define WTF 8
#define ETF 9
#define DTF 10
#define BIF 11
#define WIF 12
#define RHBF 13
#define RA1F 14
#define RA2F 15
#define RWTF 16
#define RETF 17
#define RDTF 18
#define V1F 19
#define V2F 20
#define ERF 21
#define GSF 22

static char *fext[] = {"az.dat", "uf.dat", "bc.dat", "sc.dat",
                       "nf.dat", "hb.dat", "a1.dat", "a2.dat",
                       "wt.dat", "et.dat", "dt.dat", "bi.dat",
                       "wi.dat", "rhb.dat","ra1.dat","ra2.dat",
                       "rwt.dat","ret.dat","rdt.dat","v1.dat",
                       "v2.dat", "err.dat","gsa.dat"};
char fname[NUMF][32];
FILE *fout[NUMF];

