

import os
import datetime

#wos exports grouped in subfolders
indir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data"

subfolders=os.listdir(indir)
wos_headers="PT	AU	BA	BE	GP	AF	BF	CA	TI	SO	SE	BS	LA	DT	CT	CY	CL	SP	HO	DE	ID	AB	C1	RP	EM	RI	OI	FU	FX	CR	NR	TC	Z9	PU	PI	PA	SN	EI	BN	J9	JI	PD	PY	VL	IS	PN	SU	SI	MA	BP	EP	AR	DI	D2	PG	WC	SC	GA	UT	PM"

one_saverec_file="all_years.txt"
onefile_output=open(os.path.join("/home/pgi/Documents/events/20141125_sprint_medea/",one_saverec_file),"w")
onefile_output.write(wos_headers+"\n")

nb_extra_trailing_tab=0

for root, subFolders, files in os.walk(indir):
    for file in files:
        filepath=os.path.join(root,file)
        print "merging %s"%filepath
        with open(filepath,"r") as f:
            # remove first line
            lines=f.read().split("\n")[1:]

            #and remove last character if trailing tab
            lines = [l.strip(" ") for l in lines]
            lines = [l.strip("\r") for l in lines]
            lines_=[]
            for l in lines :
                if "\t" in l:
                    # FILTERING BLANK LINES
                    if len(l.split("\t"))>60 :
                        if l[-1:]=="\t":
                            l=l[:-1] #extra tab
                            nb_extra_trailing_tab+=1
                        else:
                            print "warning fromat problem with %s"%l[-20:]
                    elif len(l.split("\t"))<60:
                        print "warning fromat problem with %s"%l[-20:]
                    lines_.append(l)
            onefile_output.write("\n".join(lines_)+"\n")
print "all files merged into %s"% one_saverec_file
print "found %s trailing extra tab"%(nb_extra_trailing_tab)

years_spans={}
onefile_output.close()
onefile_output=open(os.path.join("/home/pgi/Documents/events/20141125_sprint_medea/",one_saverec_file),"r")
onefile_output.readline()
for line in onefile_output.readlines():
    # filter blank lines
    if "\t" in line:
        y=line.split("\t")[42]
        years_spans[y]=years_spans[y]+1 if y in years_spans else 1

for y,n in sorted(((y,n) for (y,n) in years_spans.iteritems()),key=lambda a: a[0]):
    print "%s\t%s"%(y,n)


# print "%s : parsing done, start networks gen"%years
# small_thresholds={"l_thr":1,"vA":111111111,"vK":14,"vS":2,"vR":4,"vTK":20,"vY":11111111,"vC":3,"vJ":1111111,"vI":111111,"vRJ":111111111111}
# medium_thresholds={"l_thr":2,"vA":111111111,"vK":28,"vS":4,"vR":12,"vTK":40,"vY":11111111,"vC":6,"vJ":1111111,"vI":111111,"vRJ":111111111111}
# large_thresholds={"l_thr":3,"vA":111111111,"vK":56,"vS":8,"vR":36,"vTK":80,"vY":11111111,"vC":12,"vJ":1111111,"vI":111111,"vRJ":111111111111}
# medium2_thresholds={"l_thr":2,"vA":111111111,"vK":21,"vS":3,"vR":8,"vTK":30,"vY":11111111,"vC":4,"vJ":1111111,"vI":111111,"vRJ":111111111111}
# large2_thresholds={"l_thr":3,"vA":111111111,"vK":56,"vS":8,"vR":24,"vTK":80,"vY":11111111,"vC":12,"vJ":1111111,"vI":111111,"vRJ":111111111111}
# prep_het_graph(parsed_folder,network_folder,0,True,large2_thresholds)
# print "%s : network gen done, exit"%years
# return True



# pool = Pool(processes=2)

# for subfolder in sorted(subfolders):
# 	print subfolder
#  	pool.apply_async(process_wos,(os.path.join(indir,subfolder),))
# pool.close()
# pool.join()
