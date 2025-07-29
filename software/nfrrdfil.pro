;nfrreadfile.pro

function nfrreadfile, file_name, nhead, ncol, ndata

;Modified for use with /cdrom/gp_0001		MBV 10/26/98

;file_name == input,  name of file to read data from
;nhead     == input,  number of header lines
;ncol      == input,  number of columns of data
;ndata     == output, number of data lines read in

;returns array of (ncol x ndata) of type float

openr, unit, file_name, /get_lun
ndata = 0
head=""
for i=1,nhead do readf, unit, head
while (NOT eof(unit)) do begin
	readf, unit, head
	ndata = ndata + 1
endwhile

point_lun, unit, 0
data = fltarr(ncol, ndata)
if (nhead ne 0) then for i=1,nhead do readf, unit, head
readf, unit, data

free_lun, unit

return, data
end
