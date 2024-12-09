program dummyquantile
syntax varlist, level(string)

if "`level'" == "lower" {
	local pctile 33
}
elseif "`level'" == "upper" {
	local pctile 66

foreach var of varlist {
	quietly _pctile `var', p(`pctile')
	local thresh = `r(r1)'
}

end
