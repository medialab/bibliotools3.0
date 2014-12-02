import os
import itertools
import networkx
from networkx.readwrite import json_graph
import json
import codecs
from config import CONFIG

def add_edge_weight(graph, node1, node2):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += 1
    else:
        graph.add_edge(node1, node2, weight=1)


for span in sorted(CONFIG["spans"]):
	print "\n#%s"%span
	with codecs.open(os.path.join(CONFIG["parsed_data"],span,"references.dat"),"r",encoding="UTF-8") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
		
	references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
	print "%s ref occurences in articles"%len(references_by_articles)
	references_by_articles.sort(key=lambda e:e[1])
	del(data_lines)
	# filter ref which occurs un only one article
	references_article_grouped=[(reference,list(ref_arts)) for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1])]
	references_occs=dict([(reference,len(list(ref_arts))) for reference,ref_arts in references_article_grouped if len(ref_arts)>=CONFIG["spans"][span]["references"]["occ"]])
	print "filtering references"
	references_by_articles_filtered = [t for _ in (ref_arts for ref,ref_arts in references_article_grouped if len(ref_arts)>=CONFIG["spans"][span]["references"]["occ"]) for t in _]
	
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
			g.add_node(r1,type="references",occurence_count=references_occs[r1])
			g.add_node(r2,type="references",occurence_count=references_occs[r2])
			add_edge_weight(g,r1,r2)
	print "remove edges with weight < %s"%CONFIG["spans"][span]["references"]["weight"]
	g.remove_edges_from((r1,r2) for (r1,r2,d) in g.edges(data=True) if d['weight'] <CONFIG["spans"][span]["references"]["weight"])
	print "remove nodes with degree = 0"
	g.remove_nodes_from(r for (r,d) in g.degree_iter() if d <1)
	networkx.set_node_attributes(g, 'type', "reference")
	
	if CONFIG["export_ref_format"] =="gexf":
		print "write gexf export"
		networkx.write_gexf(g,os.path.join(CONFIG["parsed_data"],span,"%s.gexf"%span),encoding="UTF-8")
	elif CONFIG["export_ref_format"] == "edgelist":
		print "write csv export"
		networkx.write_weighted_edgelist(g,os.path.join(CONFIG["parsed_data"],span,"%s.csv"%span),delimiter="\t")
	elif CONFIG["export_ref_format"] == "pajek":
		print "write pajek export"
		networkx.write_pajek(g,os.path.join(CONFIG["parsed_data"],span,"%s.net"%span),encoding='UTF-8')
	elif CONFIG["export_ref_format"] == "json":
		print "write json export"
		data = json_graph.node_link_data(g)
		json.dump(data,open(os.path.join(CONFIG["parsed_data"],span,"%s.json"%span),"w"),encoding='UTF-8')
	else:
		print  "no export compatible export format specified"


