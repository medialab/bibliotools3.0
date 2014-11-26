
import os

corpus_parsed_dir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"

for span in sorted(os.listdir(corpus_parsed_dir)):
	print "#%s"%span
	# dat file have one trailing blank line at end of file

	print "- number of articles : %s"%(len(open(os.path.join(corpus_parsed_dir,span,"articles.dat"),"r").read().split("\n"))-1)
	
	authors_by_articles=open(os.path.join(corpus_parsed_dir,span,"authors.dat"),"r").read().split("\n")
	authors = set(aba.split("\t")[-1] for aba in authors_by_articles)
	print "- number of authors : unique %s total links with articles %s"%(len(authors)-1,len(authors_by_articles)-1)
	
	countries_by_articles=open(os.path.join(corpus_parsed_dir,span,"countries.dat"),"r").read().split("\n")
	countries = set(aba.split("\t")[-1] for aba in countries_by_articles)
	print "- number of countries : unique %s total links with articles %s"%(len(countries)-1,len(countries_by_articles)-1)
	
	institutions_by_articles=open(os.path.join(corpus_parsed_dir,span,"institutions.dat"),"r").read().split("\n")
	institutions = set(aba.split("\t")[-1] for aba in institutions_by_articles)
	print "- number of institutions : unique %s total links with articles %s"%(len(institutions)-1,len(institutions_by_articles)-1)

	keywords_by_articles=open(os.path.join(corpus_parsed_dir,span,"keywords.dat"),"r").read().split("\n")
	keywords = set(aba.split("\t")[-1] for aba in keywords_by_articles)
	print "- number of keywords : unique %s total links with articles %s"%(len(keywords)-1,len(keywords_by_articles)-1)

	references_by_articles=open(os.path.join(corpus_parsed_dir,span,"references.dat"),"r").read().split("\n")
	references = set(aba.split("\t")[-1] for aba in references_by_articles)
	print "- number of references : unique %s total links with articles %s"%(len(references)-1,len(references_by_articles)-1)

	subjects_by_articles=open(os.path.join(corpus_parsed_dir,span,"subjects.dat"),"r").read().split("\n")
	subjects = set(aba.split("\t")[-1] for aba in subjects_by_articles)
	print "- number of subjects : unique %s total links with articles %s"%(len(subjects)-1,len(subjects_by_articles)-1)
	