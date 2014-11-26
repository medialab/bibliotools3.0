import os
import itertools
import networkx

corpus_parsed_dir="/home/pgi/Documents/events/20141125_sprint_medea/bibtools-data-parsed"

spans={
	"pre-AR1":{"ref_occ_min":2},
	"pre-AR2":{"ref_occ_min":2},
	"pre-AR3":{"ref_occ_min":3},
	"pre-AR4":{"ref_occ_min":4},
	"pre-AR5":{"ref_occ_min":10}
}

def add_edge_weight(graph, node1, node2):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += 1
    else:
        graph.add_edge(node1, node2, weight=1)


for span in sorted(os.listdir(corpus_parsed_dir)):
	print "\n#%s"%span
	with open(os.path.join(corpus_parsed_dir,span,"references.dat"),"r") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
		
		references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
		print "%s ref occurences in articles"%len(references_by_articles)
		references_by_articles.sort(key=lambda e:e[1])
		del(data_lines)
		# filter ref which occurs un only one article
		ref_to_keep = [reference for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1]) if len(list(ref_arts))>spans[span]["ref_occ_min"]]
		ref_to_trash = [reference for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1]) if len(list(ref_arts))<=spans[span]["ref_occ_min"]]
		print "filtering reference occ at minimum %s results in removing %s on %s %03.1f%%"%(spans[span]["ref_occ_min"],len(ref_to_trash),len(ref_to_keep)+len(ref_to_trash),100*float(len(ref_to_trash))/(len(ref_to_keep)+len(ref_to_trash))) 
		#group by articles and create ref network
		g=networkx.Graph()
		# sort on article
		references_by_articles.sort(key=lambda e:e[0])
		# group by article
		print "processing edges... (go for a tea)"
		for article,art_refs in itertools.groupby(((a,r) for a,r in references_by_articles if r in ref_to_keep),key=lambda e:e[0]):
			#one link between ref cited by same article
			for r1,r2 in itertools.combinations((r for a,r in art_refs),2):
				add_edge_weight(g,r1,r2)
		print "remove edges with weight = 1"
		g.remove_edges_from((r1,r2) for (r1,r2,d) in g.edges(data=True) if d['weight'] >1)
		print "write gexf"
		networkx.write_gexf(g,os.path.join(corpus_parsed_dir,span,"%s.gexf"%span))


