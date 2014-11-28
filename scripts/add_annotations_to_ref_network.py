
import os
import networkx
import itertools
from networkx.readwrite import json_graph
import json
import codecs
import md5

# configuration
corpus_parsed_dir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"
spans={
	"process_verbose":False,
	"report_verbose":True,
	"report_csv":True,
	"pre-AR1":{
		"references":{"occ":0,"weight":1},
		"subjects":{"occ":0,"weight":1},
		"authors":{"occ":2,"weight":1},
		"institutions":{"occ":2,"weight":1},
		"keywords":{"occ":2,"weight":1},
		"countries":{"occ":2,"weight":1},
	},
	"pre-AR2":{
		"references":{"occ":2,"weight":1},
		"subjects":{"occ":0,"weight":1},
		"authors":{"occ":2,"weight":3},
		"institutions":{"occ":2,"weight":2},
		"keywords":{"occ":2,"weight":3},
		"countries":{"occ":2,"weight":2},
	},
	"pre-AR3":{
		"references":{"occ":3,"weight":1},
		"subjects":{"occ":0,"weight":1},
		"authors":{"occ":2,"weight":4},
		"institutions":{"occ":2,"weight":4},
		"keywords":{"occ":2,"weight":4},
		"countries":{"occ":2,"weight":2},
	},
	"pre-AR4":{
		"references":{"occ":4,"weight":1},
		"subjects":{"occ":0,"weight":1},
		"authors":{"occ":2,"weight":5},
		"institutions":{"occ":2,"weight":6},
		"keywords":{"occ":2,"weight":6},
		"countries":{"occ":2,"weight":3},
	},
	"pre-AR5":{
		"references":{"occ":10,"weight":2},
		"subjects":{"occ":0,"weight":1},
		"authors":{"occ":2,"weight":10},
		"institutions":{"occ":2,"weight":13},
		"keywords":{"occ":2,"weight":12},
		"countries":{"occ":2,"weight":7},
	}
}
import_format="gexf" # possible values : edgelist OR gexf
export_format="no"

def add_edge_weight(graph, node1, node2,weight=1):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += weight
    else:
        graph.add_edge(node1, node2, weight=weight)

def add_annotations(items_name,references_article_grouped,g):
	nb_nodes_before=len(g.nodes())
	# add item category
	with codecs.open(os.path.join(corpus_parsed_dir,span,"%s.dat"%items_name),"r",encoding="UTF-8") as items_file:
		articles_items=[(l.split("\t")[0],l.split("\t")[-1]) for l in items_file.read().split("\n")[:-1]]
		if spans["process_verbose"] : print "imported %s"%items_name
		
	# grouping by item
	articles_items.sort(key=lambda e:e[1])
	item_articles_grouped=[(item,list(items_arts)) for item,items_arts in itertools.groupby(articles_items,key=lambda e:e[1])]
	# filtering by occ
	article_items = [t for _ in (items_arts for item,items_arts in item_articles_grouped if len(items_arts)>=spans[span][items_name]["occ"]) for t in _]
	if spans["report_verbose"] :print "filtered %s by occ>=%s"%(items_name,spans[span][items_name]["occ"])

	# grouping by article
	article_items.sort(key=lambda e:e[0])
	article_items = dict((a,list(s for _,s in a_s )) for (a,a_s) in itertools.groupby(article_items,key=lambda e:e[0]) )
	if spans["process_verbose"] : print "%s grouped by articles"%items_name

	for r,r_as in references_article_grouped:
		# print r_as
		items = [s for ss in (article_items[a] for a,_ in r_as if a in article_items) for s in ss]
		items.sort()
		
		items_grouped=((s, len(list(vs))) for s,vs in itertools.groupby(items))
		items_filtered=[(s,nb) for s,nb in items_grouped if nb>=spans[span][items_name]["weight"]]
		
		if len(items_filtered)>0:
			g.add_nodes_from((s for s,nb in items_filtered),label=s,type=items_name)
			for s,w in items_filtered:
				add_edge_weight(g,r,s,w)

	if spans["process_verbose"] : print "remove nodes with degree = 0"
	g.remove_nodes_from(n for (n,d) in g.degree_iter() if d <1)
	nb_items_added=len(g.nodes())-nb_nodes_before
	if spans["report_verbose"] : print "added %s %s nodes in network"%(nb_items_added,items_name)
	spans[span][items_name]["occ_filtered"]=nb_items_added
	return g

if spans["report_csv"]:
	line=["span","nb references"]
	for items in ["subjects","authors","institutions","keywords","countries"]:
			line+=["f %s"%items,"nb %s"%items,"p %s"%items]
	csv_export=[]
	csv_export.append(",".join(line))

for span in sorted([n for n in os.listdir(corpus_parsed_dir) if os.path.isdir(os.path.join(corpus_parsed_dir, n)) ]):
	if spans["process_verbose"] or spans["report_verbose"] : print "\n#%s"%span

	g=networkx.Graph()
	if import_format =="gexf":
		if spans["process_verbose"] : print "read gexf"
		g=networkx.read_gexf(os.path.join(corpus_parsed_dir,span,"%s.gexf"%span),node_type=unicode)
	elif import_format == "edgelist":
		if spans["process_verbose"] : print "read csv export"
		g=networkx.read_weighted_edgelist(os.path.join(corpus_parsed_dir,span,"%s.csv"%span),delimiter="\t")
	elif import_format == "pajek":
		if spans["process_verbose"] : print "read pajek export"
		g=networkx.read_pajek(os.path.join(corpus_parsed_dir,span,"%s.csv"%span))
	elif import_format == "json":
		if spans["process_verbose"] : print "read pajek export"
		data=json.load(open(os.path.join(corpus_parsed_dir,span,"%s.json"%span),"r"),encoding="UTF-8")
		g=json_graph.node_link_graph(data)
	else:
		print  "no export copatible export format specified"
		exit(1)

	network_references=g.nodes()

	if spans["report_verbose"] : print "load %s ref from graph"%len(network_references)
	spans[span]["references"]["occ_filtered"]=len(network_references)

	with codecs.open(os.path.join(corpus_parsed_dir,span,"references.dat"),"r",encoding="UTF-8") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
	references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
	#references_by_articles_filtered=[(a,r) for a,r in references_by_articles if r in references] 

	references_by_articles.sort(key=lambda e:e[1])
	article_groupby_reference=((reference,list(ref_arts)) for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1]))
	references_article_grouped=[t for t in article_groupby_reference if len(t[1])>=spans[span]["references"]["occ"]]
	#make sure we have same references than network
	ref_filtered=[r for r,_ in references_article_grouped]
	if(len(ref_filtered))!=len(network_references):
		s1=set(ref_filtered)
		s2=set(network_references)
		to_remove = s1 - s2
		if len(to_remove)>0:
			if spans["report_verbose"] : print "filtering ref which are not in original network : removing %s ref"%len(to_remove)
			references_article_grouped=[ (r,ref_arts) for r,ref_arts in references_article_grouped if r not in to_remove]

	# print references_article_grouped
	if spans["report_verbose"] : print "imported, filtered and grouped references by articles"

	add_annotations("subjects",references_article_grouped,g)
	add_annotations("authors",references_article_grouped,g)
	add_annotations("institutions",references_article_grouped,g)
	add_annotations("keywords",references_article_grouped,g)
	add_annotations("countries",references_article_grouped,g)


	if spans["report_verbose"] : print "have now %s nodes"%len(g.nodes())
	if export_format =="gexf":
		if spans["process_verbose"] : print "write gexf export"
		networkx.write_gexf(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.gexf"%span))
	elif export_format == "edgelist":
		if spans["process_verbose"] : print "write csv export"
		networkx.write_weighted_edgelist(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.csv"%span),delimiter="\t")
	elif export_format == "pajek":
		if spans["process_verbose"] : print "write pajek export"
		networkx.write_pajek(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.net"%span))
	elif export_format == "graphml":
		if spans["process_verbose"] : print "write pajek export"
		networkx.write_graphml(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.graphml"%span))
	else:
		print  "no compatible export format specified"

	if spans["report_csv"]:
		line=[span]
		nb_ref=spans[span]["references"]["occ_filtered"]
		line.append(nb_ref)
		for items in ["subjects","authors","institutions","keywords","countries"]:
			f=spans[span][items]["weight"]
			nb=spans[span][items]["occ_filtered"]
			p="%04.1f"%(float(nb)/nb_ref*100)
			line+=[f,nb,p]
		csv_export.append(",".join(str(_) for _ in line))

if spans["report_csv"]:
	with open(os.path.join(corpus_parsed_dir,"filtering_report.csv"),"w") as csvfile:
		csvfile.write("\n".join(csv_export))
