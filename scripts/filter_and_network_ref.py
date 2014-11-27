import os
import itertools
import networkx
from networkx.readwrite import json_graph
import json
import codecs

# configuration
corpus_parsed_dir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"
spans={
	"pre-AR1":{"ref_occ_min":0,"ref_link_weight_min":0},
	"pre-AR2":{"ref_occ_min":2,"ref_link_weight_min":1},
	"pre-AR3":{"ref_occ_min":3,"ref_link_weight_min":1},
	"pre-AR4":{"ref_occ_min":4,"ref_link_weight_min":1},
	"pre-AR5":{"ref_occ_min":10,"ref_link_weight_min":2}
}
export_format="gexf" # possible values : edgelist OR gexf OR pajek

def add_edge_weight(graph, node1, node2):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += 1
    else:
        graph.add_edge(node1, node2, weight=1)


for span in sorted(os.listdir(corpus_parsed_dir)):
	print "\n#%s"%span
	with codecs.open(os.path.join(corpus_parsed_dir,span,"references.dat"),"r",encoding="UTF-8") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
		
	references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
	print "%s ref occurences in articles"%len(references_by_articles)
	references_by_articles.sort(key=lambda e:e[1])
	del(data_lines)
	# filter ref which occurs un only one article
	references_article_grouped=[(reference,list(ref_arts)) for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1])]
	print "filtering references"
	references_by_articles_filtered = [t for _ in (ref_arts for ref,ref_arts in references_article_grouped if len(ref_arts)>=spans[span]["ref_occ_min"]) for t in _]
	
	#print "filtering reference occ at minimum %s results in removing %s on %s %03.1f%%"%(spans[span]["ref_occ_min"],len(ref_to_trash),len(references_article_grouped),100*float(len(ref_to_trash))/(len(ref_to_keep)+len(ref_to_trash))) 
	#group by articles and create ref network
	
	# sort on article
	print "sorting references"
	references_by_articles_filtered.sort(key=lambda e:e[0])
	# group by article
	print "processing edges for references... (go for a tea)"
	g=networkx.Graph()
	for article,art_refs in itertools.groupby(references_by_articles_filtered,key=lambda e:e[0]):
		#one link between ref cited by same article
		for r1,r2 in itertools.combinations((r for a,r in art_refs),2):
			add_edge_weight(g,r1,r2)
	print "remove edges with weight < %s"%spans[span]["ref_link_weight_min"]
	g.remove_edges_from((r1,r2) for (r1,r2,d) in g.edges(data=True) if d['weight'] <spans[span]["ref_link_weight_min"])
	print "remove nodes with degree = 0"
	g.remove_nodes_from(r for (r,d) in g.degree_iter() if d <1)
	networkx.set_node_attributes(g, 'type', "reference")
	if export_format =="gexf":
		print "write gexf export"
		networkx.write_gexf(g,os.path.join(corpus_parsed_dir,span,"%s.gexf"%span),encoding="UTF-8")
	elif export_format == "edgelist":
		print "write csv export"
		networkx.write_weighted_edgelist(g,os.path.join(corpus_parsed_dir,span,"%s.csv"%span),delimiter="\t")
	elif export_format == "pajek":
		print "write pajek export"
		networkx.write_pajek(g,os.path.join(corpus_parsed_dir,span,"%s.net"%span),encoding='UTF-8')
	elif export_format == "json":
		print "write json export"
		data = json_graph.node_link_data(g)
		json.dump(data,open(os.path.join(corpus_parsed_dir,span,"%s.json"%span),"w"),encoding='UTF-8')
	else:
		print  "no export copatible export format specified"


