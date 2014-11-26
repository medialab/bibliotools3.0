import os
from parser import Wos_parser

indir="/home/pgi/Documents/events/20141125_sprint_medea/"
outdir_prefix= "/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"
one_saverec_file="all_years.txt"
wos_headers="PT	AU	BA	BE	GP	AF	BF	CA	TI	SO	SE	BS	LA	DT	CT	CY	CL	SP	HO	DE	ID	AB	C1	RP	EM	RI	OI	FU	FX	CR	NR	TC	Z9	PU	PI	PA	SN	EI	BN	J9	JI	PD	PY	VL	IS	PN	SU	SI	MA	BP	EP	AR	DI	D2	PG	WC	SC	GA	UT	PM"

years_spans={
	"pre-AR1":[1970,1989],
	"pre-AR2":[1990,1994],
	"pre-AR3":[1995,2000],
	"pre-AR4":[2001,2006],
	"pre-AR5":[2007,2013]
}


output_dir="by_AR"
if not os.path.exists(os.path.join(indir,output_dir)):
	os.mkdir(os.path.join(indir,output_dir))
	
files={}
for (l,ys) in years_spans.iteritems():
	if not os.path.exists(os.path.join(indir,output_dir,l)):
		os.mkdir(os.path.join(indir,output_dir,l))
	if os.path.exists(os.path.join(indir,output_dir,l,l)+".txt"):
		os.remove(os.path.join(indir,output_dir,l,l)+".txt")
	files[l]=open(os.path.join(indir,output_dir,l,l)+".txt","w")
	files[l].write(wos_headers+"\n")

onefile_output=open(os.path.join(indir,one_saverec_file),"r")
onefile_output.readline()
for line in onefile_output.readlines():
	# filter blank lines
	if "\t" in line:
		try:
			y=int(line.split("\t")[42])
			find=0
			for (l,ys) in years_spans.iteritems():
				if y >= ys[0] and y<= ys[1]:
					files[l].write(line)
					find=1
		
		except : 
			print "oups year %s can't be cat to int "%y

for (l,ys) in years_spans.iteritems():
	files[l].close()
	if not os.path.exists(os.path.join(outdir_prefix,l)):
		os.mkdir(os.path.join(outdir_prefix,l))
	Wos_parser(os.path.join(indir,output_dir,l),os.path.join(outdir_prefix,l),True)