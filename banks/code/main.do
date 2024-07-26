

// global banksdir "~/Library/Mobile Documents/com~apple~CloudDocs/svb_shock/banks"
global banksdir "C:\Users\akbri\iCloudDrive\svb_shock\banks"
* global banksdir "${projdir}/banks"

global codedir "${banksdir}/code"
global datadir "${banksdir}/data"
global tempdir "${banksdir}/temp"
global outdir "${banksdir}/output"

cap mkdir "${tempdir}"
cap mkdir "${outdir}"

do "${codedir}/clean_sod.do"
do "${codedir}/prepare_relationships.do"
