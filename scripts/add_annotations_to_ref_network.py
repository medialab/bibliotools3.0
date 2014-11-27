
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
	"pre-AR1":{"ref_occ_min":2,"ref_link_weight_min":1},
	"pre-AR2":{"ref_occ_min":2,"ref_link_weight_min":1},
	"pre-AR3":{"ref_occ_min":3,"ref_link_weight_min":1},
	"pre-AR4":{"ref_occ_min":4,"ref_link_weight_min":1},
	"pre-AR5":{"ref_occ_min":10,"ref_link_weight_min":2}
}
import_format="gexf" # possible values : edgelist OR gexf
export_format="graphml"

def add_edge_weight(graph, node1, node2,weight=1):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += weight
    else:
        graph.add_edge(node1, node2, weight=weight)




for span in sorted(os.listdir(corpus_parsed_dir))[:2]:
	print "\n#%s"%span

	g=networkx.Graph()
	if import_format =="gexf":
		print "read gexf"
		g=networkx.read_gexf(os.path.join(corpus_parsed_dir,span,"%s.gexf"%span))
	elif import_format == "edgelist":
		print "read csv export"
		g=networkx.read_weighted_edgelist(os.path.join(corpus_parsed_dir,span,"%s.csv"%span),delimiter="\t")
	elif import_format == "pajek":
		print "read pajek export"
		g=networkx.read_pajek(os.path.join(corpus_parsed_dir,span,"%s.csv"%span))
	elif import_format == "json":
		print "read pajek export"
		data=json.load(open(os.path.join(corpus_parsed_dir,span,"%s.json"%span),"r"),encoding="UTF-8")
		g=json_graph.node_link_graph(data)
	else:
		print  "no export copatible export format specified"

	
	references=[codecs.decode(n,"UTF-8") for n in g.nodes()]

	print "load %s ref from graph"%len(references)

	with codecs.open(os.path.join(corpus_parsed_dir,span,"references.dat"),"r",encoding="UTF-8") as file:
		# dat file have one trailing blank line at end of file
		data_lines=file.read().split("\n")[:-1]
	references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
	references_by_articles_filtered=[(a,r) for a,r in references_by_articles if r in references] 

	references_by_articles_filtered.sort(key=lambda e:e[1])
	references_article_grouped=[(reference,list(ref_arts)) for reference,ref_arts in itertools.groupby(references_by_articles_filtered,key=lambda e:e[1])]
	# print references_article_grouped
	print "imported, filtered and grouped references by articles"

	# # add subject category
	with codecs.open(os.path.join(corpus_parsed_dir,span,"subjects.dat"),"r",encoding="UTF-8") as subjects_file:
		article_subject=[(l.split("\t")[0],l.split("\t")[1]) for l in subjects_file.read().split("\n")[:-1]]
		article_subject.sort(key=lambda e:e[0])
		# group by article
		article_subjects = dict((a,list(s for _,s in a_s )) for (a,a_s) in itertools.groupby(article_subject,key=lambda e:e[0]))	
		# print "imported subjects"
		
		for r,r_as in references_article_grouped:
			# print r_as
			subjects = [s for ss in (article_subjects[a] for a,_ in r_as if a in article_subjects) for s in ss]
			subjects.sort()
			
			subjects_grouped=((s, len(list(vs))) for s,vs in itertools.groupby(subjects))
			subjects_filtered=[(s,nb) for s,nb in subjects_grouped if nb>=2]
			if len(subjects_filtered)>0:
				g.add_nodes_from((s for s,nb in subjects_filtered),label=s,type="subject")
				for s,w in subjects_filtered:
					add_edge_weight(g,r,s,w)
	
	# print "remove nodes with degree = 0"
	g.remove_nodes_from(n for (n,d) in g.degree_iter() if d <1)
	print "have now %s nodes"%len(g.nodes())
	if export_format =="gexf":
		print "write gexf export"
		networkx.write_gexf(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.gexf"%span))
	elif export_format == "edgelist":
		print "write csv export"
		networkx.write_weighted_edgelist(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.csv"%span),delimiter="\t")
	elif export_format == "pajek":
		print "write pajek export"
		networkx.write_pajek(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.net"%span))
	elif export_format == "graphml":
		print "write pajek export"
		networkx.write_graphml(g,os.path.join(corpus_parsed_dir,span,"%s_annotated.graphml"%span))
	else:
		print  "no export copatible export format specified"