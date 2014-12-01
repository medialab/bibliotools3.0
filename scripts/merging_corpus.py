import os
import datetime
from config import CONFIG

#preparing the one file corpus
one_file_corpus=CONFIG["one_file_corpus"]
onefile_output=open(one_file_corpus,"w")
wos_headers=CONFIG["wos_headers"]
onefile_output.write(wos_headers+"\n")

# check reports_directory
reports_directory=CONFIG["reports_directory"]
if not os.path.exists(reports_directory):
    os.mkdir(reports_directory)
elif not os.path.isdir(reports_directory):
    print "remove file %s or change reports_directory value in config"%reports_directory
    exit()

errorsfile_output=open(os.path.join(reports_directory,"wos_lines_with_errors.csv"),"w")
errorsfile_output.write(wos_headers+"\n")

nb_values_in_wos=len(wos_headers.split("\t"))

# walk the many files in wos corpus
nb_extra_trailing_tab=0
for root, subFolders, files in os.walk(CONFIG["wos_data"]):
    for file in files:
        filepath=os.path.join(root,file)
        print "merging %s"%filepath
        with open(filepath,"r") as f:
            # remove first line containing headers
            lines=f.read().split("\n")[1:]

            #and remove last character if trailing tab
            lines = [l.strip(" ") for l in lines]
            lines = [l.strip("\r") for l in lines]
            lines_=[]
            lines_with_errors=[]
            for l in lines :
                if "\t" in l:
                    # FILTERING BLANK LINES
                    if len(l.split("\t"))>nb_values_in_wos :
                        if l[-1]=="\t":
                            lines_.append(l[:-1]) #stripping extra tab
                            nb_extra_trailing_tab+=1
                        else:
                            print "warning too many columns with %s"%l[-20:]
                            lines_with_errors.append(l)
                    elif len(l.split("\t"))<nb_values_in_wos:
                        print "warning too few columns with %s"%l[-20:]
                        lines_with_errors.append(l)
                    else:
                        lines_.append(l)
            onefile_output.write("\n".join(lines_)+"\n")
            errorsfile_output.write("\n".join(lines_with_errors)+"\n")

print "all files merged into %s"% one_file_corpus
print "repaired %s lines with trailing extra tab"%(nb_extra_trailing_tab)
print "found %s lines with extra/too few columns all merged into wos_lines_with_errors.csv"%(len(lines_with_errors))

# output the articles number by years
years_spans={}
onefile_output.close()
onefile_output=open(one_file_corpus,"r")
# remove headers
onefile_output.readline()
for line in onefile_output.readlines():
    # filter blank lines
    if "\t" in line:
        # get year
        y=line.split("\t")[42]
        # increment
        years_spans[y]=years_spans[y]+1 if y in years_spans else 1

# years distribution
years_distribution=open(os.path.join(reports_directory,"years_distribution.csv"),"w")
years_distribution.write("year,nb_articles\n")
print "year,nb_articles"
for y,n in sorted(((y,n) for (y,n) in years_spans.iteritems()),key=lambda a: a[0]):
    years_distribution.write("%s,%s\n"%(y,n))
    print "%s,%s"%(y,n)
print "years distribution reported in %s"%os.path.join(reports_directory,"years_distribution.csv") 