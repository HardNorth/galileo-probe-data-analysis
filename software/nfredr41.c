/*
**	nfredr4.c
**
**	Program to read SDM tape files and extract NFR instrument data.
**	Writes several (read MANY) files of data components.
**	Writes raw counts for temp transducers, and more HK data.
**	Now writes data files more compatible with PDS archive
**	requirements.
**	Uses counts+0.5 for housekeeping value conversions
**
**	Begun 1/14/93 by PMF (UW)
**	Last modified 2/3/97 by PMF (UW)
**	Adding time after MF0, 11/11/97 PMF, ver nfredr41.c
*/

#include <stdio.h>
#include <fcntl.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "nfredr4.h"

void getmf(int fd, MF *mfp, int *sync, int *zeros, int *end);
void readDC(int fd, MF DCofMF[], int *fullDC, int *firstDC, 
	int *nosync, int *zeros, int *end);
void copyDC(MF DCofMF[], DCRaw *rawDC, int *nsubcom, long syncmf);
void convertDC(DCRaw rawDC, DCEng *engDC);
void printDC(DCEng engDC);
int getgain(int mode, int chan, int mult);
float eng_hk(int hk_id, int dig_hk);     
void prt_out(DCEng engDC, DCRaw rawDC);
void lot_out(DCEng engDC);

int DC=-1;
long RECLEN;

void main(int argc, char *argv[])
{
	int fd, sync, zeros, end;
	MF *mfp, DCofMF[31];
	DCRaw rawDC;
	DCEng engDC;
	int nosync, firstDC, fullDC, nsubcom;
	long syncmf;
	int i, j;
	char basename[32];
	char *chan_string;
	char *ts;
	time_t tp;

	/*
	**	try to open file with edr tape data
	*/
	if (argc < 3) {
		printf("usage: nfredr4 filename basename [RECLEN]\n");
		exit(1);
	}

	if (argc == 4) {
		RECLEN = (long) atoi(argv[3]);
		printf("using record length of %ld\n", RECLEN);
	} else {
		RECLEN = 100;
		printf("using record length of %ld\n", RECLEN);
	}

	if ((fd=open(argv[1], O_RDONLY, 0)) == -1) {
		printf("could not open file %s\n", argv[1]);
		exit(1);
	}
	strcpy(basename, argv[2]);

	/*
	** open output files and print file headers
	*/

	time(&tp);
	ts = ctime(&tp);
	for (i=0; i<NUMF; i++) {
		strcpy(fname[i], basename);
		strcat(fname[i], fext[i]);
		/* printf("%s\n", fname[i]); */
		if ((fout[i] = fopen(fname[i],"w")) == NULL) {
			fprintf(stderr,"couldn't open %s\n",fname[i]);
			exit(1);
		}
		fprintf(fout[i],"%s created from %s\n",
			fname[i], argv[1]);
		fprintf(fout[i],"Creation time: %s", ts);
	}
	chan_string="_A  B  C  D  E  F";
	fprintf(fout[NFF],"DC  IC  T(SEC)  NF%s\n",chan_string);
	fprintf(fout[SCF],"DC  IC  T(SEC)  SC%s\n",chan_string);
	fprintf(fout[AZF],"DC  IC  T(SEC)  AZ%s\n",chan_string);
	fprintf(fout[UFF],"DC  IC  T(SEC)  UF%s\n",chan_string);
	fprintf(fout[BCF],"DC  IC  T(SEC)  BC%s\n",chan_string);
	fprintf(fout[HBF],"DC  IC  T(SEC)  HB(C)\n");
	fprintf(fout[A1F],"DC  IC  T(SEC)  A1(C)\n");
	fprintf(fout[A2F],"DC  IC  T(SEC)  A2(C)\n");
	fprintf(fout[WTF],"DC  IC  T(SEC)  WT(C)\n");
	fprintf(fout[ETF],"DC  IC  T(SEC)  ET(C)\n");
	fprintf(fout[DTF],"DC  IC  T(SEC)  DT(C)\n");
	fprintf(fout[BIF],"DC  IC  T(SEC)  BI\n");
	fprintf(fout[WIF],"DC  IC  T(SEC)  WI\n");
	fprintf(fout[RHBF],"DC  IC  T(SEC)  HB(DN)\n");
	fprintf(fout[RA1F],"DC  IC  T(SEC)  A1(DN)\n");
	fprintf(fout[RA2F],"DC  IC  T(SEC)  A2(DN)\n");
	fprintf(fout[RWTF],"DC  IC  T(SEC)  WT(DN)\n");
	fprintf(fout[RETF],"DC  IC  T(SEC)  ET(DN)\n");
	fprintf(fout[RDTF],"DC  IC  T(SEC)  DT(DN)\n");
	fprintf(fout[V1F],"DC  IC  T(SEC)  V1(V)\n");
	fprintf(fout[V2F],"DC  IC  T(SEC)  V2(V)\n");
	fprintf(fout[ERF],"DC  IC  T(SEC)  ERR\n");
	fprintf(fout[GSF],"DC  IC  T(SEC)  GSA_CAL\n");



	mfp = (MF *) malloc(sizeof(MF));
	nosync = True;
	end = False;
	while (end != True) {
		/*
		**	skip to sync frame or end
		*/
		while (nosync == True) {
			getmf(fd, mfp, &sync, &zeros, &end);
			if (end == True) {
				close(fd);
				exit(0);
			}
			if (sync == True) {
				nosync = False;
				syncmf = mfp->mfnum;
				firstDC = True;
				nsubcom = BI;
			}
		} 
		/*
		**	get a data cycle of minor frames
		*/
		readDC(fd, &DCofMF[0], &fullDC, &firstDC, &nosync, 
			&zeros, &end);
		/* if (fullDC == False)
			continue; */
		/*
		**	copy DC of MF's to DC of IC's
		*/
		copyDC(DCofMF, &rawDC, &nsubcom, syncmf);
		convertDC(rawDC, &engDC);
		DC++;
		prt_out(engDC, rawDC);
	}
	close(fd);
} /* end of main */


void getmf(int fd, MF *mfp, int *sync, int *zeros, int *end)
/*
**	Reads a minor frame from data file, sets zeros if all
**	nfr data bytes were 0, sync if they were 0x76, end if
**	end of file is reached.
*/
{
	unsigned char mfdata[RECMAX];
	static unsigned int mfnummsb=0;
	unsigned int mfnumlsb;
	int i;

	if (read(fd, mfdata, RECLEN) != RECLEN) {
		*end = True;
	}
	else {
		*end = False;
		mfnumlsb = mfdata[36+4] & 0x3F;
		if (mfnumlsb % 16 == 4)
			mfnummsb = mfdata[36+49];
		mfp->mfnum = (mfnummsb << 6) | mfnumlsb;
		mfp->nfrmfw[0] = mfdata[36+8];
		mfp->nfrmfw[1] = mfdata[36+9];
		mfp->nfrmfw[2] = mfdata[36+24];
		mfp->nfrmfw[3] = mfdata[36+25];
		mfp->nfrmfw[4] = mfdata[36+40];
		mfp->nfrmfw[5] = mfdata[36+41];
		mfp->nfrmfw[6] = mfdata[36+56];
		mfp->nfrmfw[7] = mfdata[36+57];
		mfp->mfw52 = mfdata[36+52];
		/* printf("mf:%2d  49:%4d  52:%4d\n",mfnumlsb%16,
			mfdata[36+52],mfdata[36+52]); */
		*zeros = True;
		*sync = True;
		for (i=0; i<8; i++) {
			if (mfp->nfrmfw[i] != 0x00)
				*zeros = False;
			if (mfp->nfrmfw[i] != 0x76)
				*sync = False;
		}
	}
}


void readDC(int fd, MF DCofMF[], int *fullDC, int *firstDC, 
	int *nosync, int *zeros, int *end)
/*
**	Reads in thirty minor frames.
*/
{
	int i, j, sync;

	*fullDC = True; 
	for (i=0; i<31; i++) {
		DCofMF[i].data_valid = True;
		if (i==0 && *firstDC == False) {
			DCofMF[0].mfnum = DCofMF[30].mfnum;
			for (j=0; j<8; j++)
				DCofMF[0].nfrmfw[j] =
					DCofMF[30].nfrmfw[j];
			DCofMF[0].mfw52 = DCofMF[30].mfw52;
		} else {
			getmf(fd, &DCofMF[i], &sync, zeros, end);
		}
		if (*zeros == True) {
			/* for (j=i; j<31; j++) */
			DCofMF[i].data_valid = False;
			/* *nosync = True; */
			*fullDC = False;
		}
		if (*end == True) {
			for (j=i; j<31; j++)
				DCofMF[j].data_valid = False;
			*fullDC = False;
		}
	}
	*firstDC = False;
}


void copyDC(MF DCofMF[], DCRaw *rawDC, int *nsubcom, long syncmf)
/*
**	Copies data from array of minor frames to array of instrument
**	cycles.
*/
{	
	int frontmf, backmf, i, j;

	rawDC->start_mf = DCofMF[0].mfnum;
	for (i=0; i<20; i++) {
		if (i % 2 == 0) {
			frontmf = (i/2)*3;
			backmf = frontmf+1;

			if (DCofMF[frontmf].data_valid == False) {
				rawDC->ic[i].data_valid = False;
				continue;
			} else if (DCofMF[backmf].data_valid == False) {
				rawDC->ic[i].data_valid = False;
				continue;
			} else
				rawDC->ic[i].data_valid = True;

			for (j=0; j<4; j++)
				rawDC->ic[i].data_wds[j] =
					DCofMF[frontmf].nfrmfw[j+4];
			for (j=4; j<12; j++)
				rawDC->ic[i].data_wds[j] =
					DCofMF[backmf].nfrmfw[j-4];
			if (((DCofMF[backmf].mfnum-syncmf+2)%4)==0) {
				rawDC->ic[i].sub_id = *nsubcom;
				rawDC->ic[i].sub_data = 
					DCofMF[backmf].mfw52;
				if (*nsubcom == BI)
					*nsubcom = WI;
				else
					*nsubcom = BI;
			} else
				rawDC->ic[i].sub_id = False;
		} else {
			frontmf = (i/2)*3+2;
			backmf = frontmf+1;

			if (DCofMF[frontmf].data_valid == False) {
				rawDC->ic[i].data_valid = False;
				continue;
			} else if (DCofMF[backmf].data_valid == False) {
				rawDC->ic[i].data_valid = False;
				continue;
			} else
				rawDC->ic[i].data_valid = True;

			for (j=0; j<8; j++)
				rawDC->ic[i].data_wds[j] =
					DCofMF[frontmf].nfrmfw[j];
			for (j=8; j<12; j++)
				rawDC->ic[i].data_wds[j] =
					DCofMF[backmf].nfrmfw[j-8];
			if (((DCofMF[frontmf].mfnum-syncmf+2)%4)==0) {
				rawDC->ic[i].sub_id = *nsubcom;
				rawDC->ic[i].sub_data = 
					DCofMF[frontmf].mfw52;
				if (*nsubcom == BI)
					*nsubcom = WI;
				else
					*nsubcom = BI;
			} else if 
			  (((DCofMF[backmf].mfnum-syncmf+2)%4)==0) {
				rawDC->ic[i].sub_id = *nsubcom;
				rawDC->ic[i].sub_data = 
					DCofMF[backmf].mfw52;
				if (*nsubcom == BI)
					*nsubcom = WI;
				else
					*nsubcom = BI;
			} else
				rawDC->ic[i].sub_id = False;
		} /* else */
	} /* for */
} /* function copyDC */


void convertDC(DCRaw rawDC, DCEng *engDC)
/*
**	Converts data cycle of raw data to engineering values.
*/
{
	int i, j, sign, mult, cnts, gain, ic;
	int gsa_sgn[6], gsa_cts[6], det_cts[6];

	engDC->start_mf = rawDC.start_mf;
	for (i=0; i<20; i++) {
	        ic = (DC+1) * 20 + i;
		if ((engDC->ic[i].data_valid = rawDC.ic[i].data_valid) == False)
			continue;

		engDC->ic[i].error = (0x80 & rawDC.ic[i].data_wds[0]) >> 7;
		engDC->ic[i].mode = (0x60 & rawDC.ic[i].data_wds[0]) >> 5;

		for (j = 0; j < 6; j++) {
			switch (j) {
			case 0:
				sign = (rawDC.ic[i].data_wds[1] & 0x80) >> 7;
				mult = (rawDC.ic[i].data_wds[1] & 0x60) >> 5;
				cnts = (rawDC.ic[i].data_wds[1] << 4 & 0x1f0) |
					(rawDC.ic[i].data_wds[2] >> 4 & 0x00f);
				break;
			case 1:
				sign = (rawDC.ic[i].data_wds[2] & 0x08) >> 3;
				mult = (rawDC.ic[i].data_wds[2] & 0x06) >> 1;
				cnts = (rawDC.ic[i].data_wds[2] << 8 & 0x100) |
					rawDC.ic[i].data_wds[3];
				break;
			case 2:
				sign = (rawDC.ic[i].data_wds[4] & 0x80) >> 7;
				mult = (rawDC.ic[i].data_wds[4] & 0x60) >> 5;
				cnts = (rawDC.ic[i].data_wds[4] << 4 & 0x1f0) |
					(rawDC.ic[i].data_wds[5] >> 4 & 0x00f);
				break;
			case 3:
				sign = (rawDC.ic[i].data_wds[5] & 0x08) >> 3;
				mult = (rawDC.ic[i].data_wds[5] & 0x06) >> 1;
				cnts = (rawDC.ic[i].data_wds[5] << 8 & 0x100) |
					rawDC.ic[i].data_wds[6];
				break;
			case 4:
				sign = (rawDC.ic[i].data_wds[7] & 0x80) >> 7;
				mult = (rawDC.ic[i].data_wds[7] & 0x60) >> 5;
				cnts = (rawDC.ic[i].data_wds[7] << 4 & 0x1f0) |
					(rawDC.ic[i].data_wds[8] >> 4 & 0x00f);
				break;
			case 5:
				sign = (rawDC.ic[i].data_wds[8] & 0x08) >> 3;
				mult = (rawDC.ic[i].data_wds[8] & 0x06) >> 1;
				cnts = (rawDC.ic[i].data_wds[8] << 8 & 0x100) |
					rawDC.ic[i].data_wds[9];
				break;
			}
			if (!sign) {
				cnts -= 1;
				cnts = -(~cnts & 0x1ff);
			}
			gain = getgain(engDC->ic[i].mode, j, mult);
			engDC->ic[i].chan_data[j] = (long) cnts * gain;
		}
		engDC->ic[i].hk_data[0] = eng_hk(hk_order[i][0],
						rawDC.ic[i].data_wds[10]);
 		if ((hk_order[i][0] == A2) && (ic >= 115))
		  engDC->ic[i].hk_data[0] = 
		    eng_hk(A2, rawDC.ic[i].data_wds[10]+256);
 		if ((hk_order[i][0] == ET) && (ic >= 94) && (ic <= 214))
		  engDC->ic[i].hk_data[0] = 
		    eng_hk(ET, rawDC.ic[i].data_wds[10]-256);
 		if ((hk_order[i][0] == ET) && (ic >= 464))
		  engDC->ic[i].hk_data[0] = 
		    eng_hk(ET, rawDC.ic[i].data_wds[10]+256);
 		if ((hk_order[i][0] == HB) && (ic >= 519))
		  engDC->ic[i].hk_data[0] = 
		    eng_hk(HB, rawDC.ic[i].data_wds[10]+256);


		engDC->ic[i].hk_data[1] = eng_hk(hk_order[i][1],
						rawDC.ic[i].data_wds[11]);
		if ((hk_order[i][1] == A2) && (ic >= 115))
		  engDC->ic[i].hk_data[1] = 
		    eng_hk(A2, rawDC.ic[i].data_wds[11]+256);

		engDC->ic[i].sub_id = rawDC.ic[i].sub_id;
		if (rawDC.ic[i].sub_id != False) {
			engDC->ic[i].sub_data = eng_hk(rawDC.ic[i].sub_id,
							rawDC.ic[i].sub_data);
		}
	}
	gsa_sgn[0] = rawDC.ic[0].data_wds[0] >> 4 & 0x01;
	gsa_cts[0] = (rawDC.ic[0].data_wds[0] << 11 & 0x6000) |
				(rawDC.ic[1].data_wds[0] << 8 & 0x1c00) |
				(rawDC.ic[2].data_wds[0] << 5 & 0x0380) |
				(rawDC.ic[3].data_wds[0] << 2 & 0x0040);
	gsa_sgn[1] = rawDC.ic[3].data_wds[0] >> 3 & 0x01;
	gsa_cts[1] = (rawDC.ic[3].data_wds[0] << 12 & 0x4000) |
				(rawDC.ic[4].data_wds[0] << 9 & 0x3800) |
				(rawDC.ic[5].data_wds[0] << 6 & 0x0700) |
				(rawDC.ic[6].data_wds[0] << 3 & 0x00c0);
	gsa_sgn[2] = rawDC.ic[6].data_wds[0] >> 2 & 0x01;
	gsa_cts[2] = (rawDC.ic[7].data_wds[0] << 7 & 0x0e00) |
				(rawDC.ic[8].data_wds[0] << 4 & 0x01c0) |
				(rawDC.ic[9].data_wds[0] << 1 & 0x0038);
	gsa_sgn[3] = rawDC.ic[10].data_wds[0] >> 4 & 0x01;
	gsa_cts[3] = (rawDC.ic[10].data_wds[0] << 8 & 0x0c00) |
				(rawDC.ic[11].data_wds[0] << 5 & 0x0380) |
				(rawDC.ic[12].data_wds[0] << 2 & 0x0070) |
				(rawDC.ic[13].data_wds[0] >> 1 & 0x0008);
	gsa_sgn[4] = rawDC.ic[13].data_wds[0] >> 3 & 0x01;
	gsa_cts[4] = (rawDC.ic[13].data_wds[0] << 6 & 0x0100) |
				(rawDC.ic[14].data_wds[0] << 3 & 0x00e0) |
				(rawDC.ic[15].data_wds[0] & 0x001c) |
				(rawDC.ic[16].data_wds[0] >> 3 & 0x0003);
	gsa_sgn[5] = rawDC.ic[16].data_wds[0] >> 2 & 0x01;
	gsa_cts[5] = (rawDC.ic[17].data_wds[0] << 4 & 0x01c0) |
				(rawDC.ic[18].data_wds[0] << 1 & 0x0038) |
				(rawDC.ic[19].data_wds[0] >> 2 & 0x0007);
	for (j = 0; j < 6; j++) {
		if (!gsa_sgn[j]) {
			if (j < 2)
				gsa_cts[j] >>= 6;
			else if (j < 4)
				gsa_cts[j] >>= 3;
			gsa_cts[j] -= 1;
			gsa_cts[j] = -(~gsa_cts[j] & 0x01ff);
			if (j < 2)
				gsa_cts[j] <<= 6;
			else if (j < 4)
				gsa_cts[j] <<= 3;
		}
		engDC->gsa_data[j] = gsa_cts[j];
	}
	det_cts[0] = (rawDC.ic[0].data_wds[0] << 6 & 0x00c0) |
				(rawDC.ic[1].data_wds[0] << 4 & 0x0030) |
				(rawDC.ic[2].data_wds[0] << 2 & 0x000c) |
				(rawDC.ic[3].data_wds[0] & 0x0003);
	det_cts[1] = (rawDC.ic[4].data_wds[0] << 6 & 0x00c0) |
				(rawDC.ic[5].data_wds[0] << 4 & 0x0030) |
				(rawDC.ic[6].data_wds[0] << 2 & 0x000c) |
				(rawDC.ic[7].data_wds[0] & 0x0003);
	det_cts[2] = (rawDC.ic[8].data_wds[0] << 6 & 0x00c0) |
				(rawDC.ic[9].data_wds[0] << 4 & 0x0030) |
				(rawDC.ic[10].data_wds[0] << 2 & 0x000c) |
				(rawDC.ic[11].data_wds[0] & 0x0003);
	det_cts[3] = (rawDC.ic[12].data_wds[0] << 6 & 0x00c0) |
				(rawDC.ic[13].data_wds[0] << 4 & 0x0030) |
				(rawDC.ic[14].data_wds[0] << 2 & 0x000c) |
				(rawDC.ic[15].data_wds[0] & 0x0003);
	det_cts[4] = (rawDC.ic[16].data_wds[0] << 6 & 0x00c0) |
				(rawDC.ic[17].data_wds[0] << 4 & 0x0030) |
				(rawDC.ic[18].data_wds[0] << 2 & 0x000c) |
				(rawDC.ic[19].data_wds[0] & 0x0003);
	for (j = 0; j < 5; j++) {
	  ic = (DC+1) * 20 + j*4;
	        engDC->rdt_data[j] = det_cts[j];
		engDC->dt_data[j] = eng_hk(DT, det_cts[j]);
		if ((ic >= 24) && (ic <= 188))
		  engDC->dt_data[j] = eng_hk(DT, det_cts[j]-256);
		if (ic >= 408)
		  engDC->dt_data[j] = eng_hk(DT, det_cts[j]+256);

	}
}

int getgain(int mode, int chan, int mult)        
		/* determines correct channel gain */
/*
**	Returns correct gain multiplier for a given channel and mode.
*/
{
	int gain;

	switch (mult) {
		case 0:
			gain = 64;
			break;
		case 1:
			gain = 8;
			break;
		case 2:
			gain = 1;
			break;
	}
	if (chan == 0 || chan == 2 || chan == 3 || chan == 5) {
		if (mode == BC) {
			gain *= 8;
		}
	}
	return(gain);
}

float eng_hk(int hk_id, int dig_hk)     
		/* converts digital to engineering units */
/*
**	This function converts raw housekeeping data into engineering units.
*/
{
	double a, b, c, Rfeedback, Rseries, vt;
	double d, r, eng_unit;
	float flt_hk;

	flt_hk = dig_hk + 0.5;
	switch (hk_id) {
		case HB:
		case A1:
		case A2:
		case WT:
			a = hk_parms[hk_id][0];
			b = hk_parms[hk_id][1];
			c = hk_parms[hk_id][2];
			Rfeedback = hk_parms[hk_id][3];
			Rseries = hk_parms[hk_id][4];
			vt = vtherm;
			d = 255.0 * Rfeedback * vt / 4.98;
			r = d / flt_hk - Rseries;
			eng_unit = 1.0 /
				(a + b*log(r) + 
				c*pow(log(r), (double) 3.0));
			eng_unit -= 273.15;
			break;
		case DT:
		case ET:
		case V1:
		case V2:
		case BI:
		case WI:
			a = hk_parms[hk_id][0];
			b = hk_parms[hk_id][1];
			eng_unit = a + b*flt_hk;
			break;
		case SW:
			a = hk_parms[hk_id][0];
			b = hk_parms[hk_id][1];
			eng_unit = a + b*dig_hk;
			break;
	}
	return((float) eng_unit);
}


/*
** prt_out
**
** Prints data to files suitable for PDS inclusion (comma-separated)
*/
void prt_out(DCEng engDC, DCRaw rawDC)
{
	int i, j, n=0;
	float t_norm, t_short, t_hk;

	/*
	** print DC of data to files
	*/
	for (i=0; i<20; i++) {
		if (engDC.ic[i].data_valid == False)
			continue;

		t_norm = DC*120.0 + i*6.0 + 6.75;
		t_short = DC*120.0 + i*6.0 + 8.25;
		t_hk = DC*120.0 + i*6.0 + 9.75;

		fprintf(fout[ERF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		fprintf(fout[ERF],"%8d\n", engDC.ic[i].error);

		/*
		** print radiometric data
		*/
		if (engDC.ic[i].mode == NF) {
		  if (i == 1 || i == 10) {
		    fprintf(fout[SCF],"%6d, %5d, %9.2f,",DC, i, t_short);
		    for (j=0; j<5; j++)
		      fprintf(fout[SCF]," %7ld,", engDC.ic[i].chan_data[j]);
		    fprintf(fout[SCF]," %7ld", engDC.ic[i].chan_data[5]);
		    fprintf(fout[SCF],"\n");
		  } else {
		    fprintf(fout[NFF],"%6d, %5d, %9.2f,",DC, i, t_norm);
		    for (j=0; j<5; j++)
		      fprintf(fout[NFF]," %7ld,", engDC.ic[i].chan_data[j]);
		    fprintf(fout[NFF]," %7ld", engDC.ic[i].chan_data[5]);
		    fprintf(fout[NFF],"\n");
		  }
		}
		if (engDC.ic[i].mode == AZ) {
		  fprintf(fout[AZF],"%6d, %5d, %9.2f,",DC, i, t_short);
		  for (j=0; j<5; j++)
		    fprintf(fout[AZF]," %7ld,", engDC.ic[i].chan_data[j]);
		  fprintf(fout[AZF]," %7ld", engDC.ic[i].chan_data[5]);
		  fprintf(fout[AZF],"\n");
		}
		if (engDC.ic[i].mode == UF) {
		  fprintf(fout[UFF],"%6d, %5d, %9.2f,",DC, i, t_norm);
		  for (j=0; j<5; j++)
		    fprintf(fout[UFF]," %7ld,", engDC.ic[i].chan_data[j]);
		  fprintf(fout[UFF]," %7ld", engDC.ic[i].chan_data[5]);
		  fprintf(fout[UFF],"\n");
		}
		if (engDC.ic[i].mode == BC) {
		  fprintf(fout[BCF],"%6d, %5d, %9.2f,",DC, i, t_norm);
		  for (j=0; j<5; j++)
		    fprintf(fout[BCF]," %7ld,", engDC.ic[i].chan_data[j]);
		  fprintf(fout[BCF]," %7ld", engDC.ic[i].chan_data[5]);
		  fprintf(fout[BCF],"\n");
		}

		/*
		** print HB, A1, A2, WT, ET, V1, V2
		*/
		for (j=0; j<=1; j++) {
			switch(hk_order[i][j]) {
				case HB:
		  			fprintf(fout[HBF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[HBF],"%10.2f",
						engDC.ic[i].hk_data[j]);
		  			fprintf(fout[HBF],"\n");
		  			fprintf(fout[RHBF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[RHBF],"%8d\n",
						rawDC.ic[i].data_wds[10+j]);
					break;
				case A1:
		  			fprintf(fout[A1F],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[A1F],"%10.2f",
						engDC.ic[i].hk_data[j]);
		  			fprintf(fout[A1F],"\n");
		  			fprintf(fout[RA1F],"%6d, %5d, %9.2f,", 
						DC, i, t_hk);
					fprintf(fout[RA1F],"%8d\n",
						rawDC.ic[i].data_wds[10+j]);
					break;
				case A2:
		  			fprintf(fout[A2F],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[A2F],"%10.2f",
						engDC.ic[i].hk_data[j]);
		  			fprintf(fout[A2F],"\n");
		  			fprintf(fout[RA2F],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[RA2F],"%8d\n",
						rawDC.ic[i].data_wds[10+j]);
					break;
				case WT:
		  			fprintf(fout[WTF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[WTF],"%10.2f",
						engDC.ic[i].hk_data[j]);
		  			fprintf(fout[WTF],"\n");
		  			fprintf(fout[RWTF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[RWTF],"%8d\n",
						rawDC.ic[i].data_wds[10+j]);
					break;
				case ET:
		  			fprintf(fout[ETF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[ETF],"%10.2f",
						engDC.ic[i].hk_data[j]);
		  			fprintf(fout[ETF],"\n");
		  			fprintf(fout[RETF],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[RETF],"%8d\n",
						rawDC.ic[i].data_wds[10+j]);
					break;
				case V1:
					fprintf(fout[V1F],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[V1F],"%10.2f\n",
						engDC.ic[i].hk_data[j]);
					break;
				case V2:
					fprintf(fout[V2F],"%6d, %5d, %9.2f,",
						DC, i, t_hk);
					fprintf(fout[V2F],"%10.2f\n",
						engDC.ic[i].hk_data[j]);
					break;
				default:
					break;
			}
		}
		
		/*
		** print DT
		*/

		if (i%4 == 0) {
			fprintf(fout[DTF],"%6d, %5d, %9.2f,",DC, i, t_hk);
			fprintf(fout[DTF],"%10.2f",
				engDC.dt_data[i/4]);
			fprintf(fout[DTF],"\n");
			fprintf(fout[RDTF],"%6d, %5d, %9.2f,",DC, i, t_hk);
			fprintf(fout[RDTF]," %8d",
				engDC.rdt_data[i/4]);
			fprintf(fout[RDTF],"\n");
		}

		/*
		** print GSA Cal numbers
		*/

		switch (i) {
		case 0:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[0]);
		  break;
		case 3:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[1]);
		  break;
		case 6:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[2]);
		  break;
		case 10:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[3]);
		  break;
		case 13:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[4]);
		  break;
		case 16:
		  fprintf(fout[GSF],"%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[GSF],"%8d\n",
			  engDC.gsa_data[5]);
		  break;
		}

		/*
		** print BI and WI
		*/

		if (rawDC.ic[i].sub_id == BI) {
		  fprintf(fout[BIF], "%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[BIF], "%10.2f\n", 
			  engDC.ic[i].sub_data);
		}
		if (rawDC.ic[i].sub_id == WI) {
		  fprintf(fout[WIF], "%6d, %5d, %9.2f,",DC, i, t_hk);
		  fprintf(fout[WIF], "%10.2f\n", 
			  engDC.ic[i].sub_data);
		}
	} /* for i */
}

