;nfrread_flux.pro

;17 March 1998, PMF
;Minimal program to read PDS flux file and interpolated pressure.
;26 October 1999, MBV
;Modified for use with both net flux and up flux files.

;Program to read either Net Flux Radiometer net flux in 
;/data/nfr/fluxes/mctcnfdn.tab, or  
;pflux fully corrected data in /data/nfr/fluxes/mctcuf.tab.
;When keyword uf is not set, the net flux file, 
;/cdrom/gp_0001/data/nfr/fluxes/mctcnfdn.tab is read.
;When keyword uf is set, the upflux file, 
;/cdrom/gp_0001/data/nfr/fluxes/mctcuf.tab is read.

pro nfrread_flux, fluxdata, press, uf = uf

if (keyword_set(uf)) then begin			;read up flux
  dir1 = '/cdrom/gp_0001/data/nfr/fluxes/'	;For uses with CDrom
  fflux = 'mctcuf.tab'
  nhead1 = 101
  ncols1 = 9
endif else begin
  ;dir1 = '~pds_ftp/data/fluxes/'		;read net flux
  dir1 = '/cdrom/gp_0001/data/nfr/fluxes/'	;For uses with CDrom
  fflux = 'mctcnfdn.tab'
  nhead1 = 100
  ncols1 = 9
endelse

;dir2 = '~pds_ftp/data/ancillar/'
dir2 = '/cdrom/gp_0001/data/asi/'	;For uses with CDrom
;fseiff = 'seiff_28may97.dat'
fseiff = 'descent.tab'
;nhead2 = 1
nhead2 = 0
ncols2 = 8

fluxdata = nfrreadfile(dir1+fflux, nhead1, ncols1, npts1)
seiffdata = nfrreadfile(dir2+fseiff, nhead2, ncols2, npts2)

nf_press = interpol(seiffdata(1,*),seiffdata(0,*),fluxdata(2,*))

;plot data just to prove this works

xr=[-15,15]
if (keyword_set(uf)) then xr=[-2,4]
yr=[15,0.4]

plot_io, xr, yr, xr=xr, /xs, yr=yr, /ys, /nodata

for i=0,5 do begin
  oplot, fluxdata(3+i, *), nf_press(*), color=50+35*i, psym=0
endfor

end
