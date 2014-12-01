import os
from parser import Wos_parser
from config import CONFIG


indir=os.path.dirname(CONFIG["one_file_corpus"])
output_dir=CONFIG["wos_data_grouped"]
if not os.path.exists(os.path.join(indir,output_dir)):
	os.mkdir(os.path.join(indir,output_dir))
outdir_prefix=CONFIG["parsed_data"]
if not os.path.exists(outdir_prefix):
	os.mkdir(outdir_prefix)

years_spans=dict((s,data["years"]) for s,data in CONFIG["spans"].iteritems())

files={}
for (l,ys) in years_spans.iteritems():
	if not os.path.exists(os.path.join(indir,output_dir,l)):
		os.mkdir(os.path.join(indir,output_dir,l))
	if os.path.exists(os.path.join(indir,output_dir,l,l)+".txt"):
		os.remove(os.path.join(indir,output_dir,l,l)+".txt")
	files[l]=open(os.path.join(indir,output_dir,l,l)+".txt","w")
	files[l].write(CONFIG["wos_headers"]+"\n")

onefile_output=open(CONFIG["one_file_corpus"],"r")
onefile_output.readline()
for line in onefile_output.readlines():
	# filter blank lines
	if "\t" in line:
		try:
			y=int(line.split("\t")[42])
			for (l,ys) in years_spans.iteritems():
				if y >= ys[0] and y<= ys[1]:
					files[l].write(line)
		
		except : 
			print "oups year %s can't be cat to int "%y

for (l,ys) in years_spans.iteritems():
	files[l].close()
	if not os.path.exists(os.path.join(outdir_prefix,l)):
		os.mkdir(os.path.join(outdir_prefix,l))
	Wos_parser(os.path.join(indir,output_dir,l),os.path.join(outdir_prefix,l),True)