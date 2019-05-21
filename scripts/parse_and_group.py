import os
from parser import Wos_parser
from config import CONFIG
import traceback


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
			year_in_PY=line.split("\t")[44]
			y=int(year_in_PY) if year_in_PY != "" else ""
			for (l,ys) in years_spans.iteritems():
				if y!= '' and y >= ys[0] and y<= ys[1]:
					files[l].write(line)
		
		except Exception as e:
			print traceback.format_exc()
			exit()

for (l,ys) in years_spans.iteritems():
	files[l].close()
	if not os.path.exists(os.path.join(outdir_prefix,l)):
		os.mkdir(os.path.join(outdir_prefix,l))
	Wos_parser(os.path.join(indir,output_dir,l),os.path.join(outdir_prefix,l),True)