import os
import itertools

corpus_parsed_dir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"

def print_statistics_of(filename):
	with open(os.path.join(corpus_parsed_dir,span,filename),"r") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
		entity_name=filename.split(".")[0]
		if filename!="references.dat":
			entities_by_articles=[aba.split("\t")[-1] for aba in data_lines]
		else:
			entities_by_articles=[",".join(aba.split("\t")[1:]) for aba in data_lines]
		unique_entities = set(entities_by_articles)
		print "- number of %s : unique %s total links with articles %s"%(entity_name,len(unique_entities),len(entities_by_articles))
		print "occ,nb_%s,cumulative %%"%(entity_name)
		occs=[len(list(g)) for (k,g) in itertools.groupby(sorted(entities_by_articles,reverse=True))]
		l=[]
		nb_occ_cumul=0
		for occ,v in itertools.groupby(sorted(occs,reverse=True)):
			nb_occ_cumul+=len(list(v))
			occ_cumul=100*float(nb_occ_cumul)/len(unique_entities)
			l.append((occ,nb_occ_cumul,occ_cumul))
		string=""
		for e in l:
			string+="%02d,%02d,%04.1f%%\n"%(e)
		print string




for span in sorted(os.listdir(corpus_parsed_dir)):
	print "\n\n#%s"%span
	with open(os.path.join(corpus_parsed_dir,span,"articles.dat"),"r") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
		print "- number of articles : %s"%len(data_lines)
	print_statistics_of("authors.dat")
	print_statistics_of("countries.dat")
	print_statistics_of("institutions.dat")
	print_statistics_of("keywords.dat")
	print_statistics_of("references.dat")
	print_statistics_of("subjects.dat")

# years_spans={
# 	"pre-AR1":{"authors":,"countries":,"institutions":,"keywords":,"references":,"subjects":},
# 	"pre-AR2":[1990,1994],
# 	"pre-AR3":[1995,2000],
# 	"pre-AR4":[2001,2006],
# 	"pre-AR5":[2007,2013]
# }
# 	