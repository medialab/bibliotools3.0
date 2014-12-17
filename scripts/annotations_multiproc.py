
import os
import networkx
import itertools
from networkx.readwrite import json_graph
import json
import codecs
from multiprocessing import Process
from multiprocessing import JoinableQueue


from config import CONFIG


def add_edge_weight(graph, node1, node2,weight=1):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += weight
    else:
        graph.add_edge(node1, node2, weight=weight)

def add_annotations(items_name,references_article_grouped,g,log):
    nb_nodes_before=len(g.nodes())
    # add item category
    with codecs.open(os.path.join(CONFIG["parsed_data"],span,"%s.dat"%items_name),"r",encoding="UTF-8") as items_file:
        articles_items=[(l.split("\t")[0],l.split("\t")[-1]) for l in items_file.read().split("\n")[:-1]]
        log("imported %s"%items_name)
    
    # grouping by item
    articles_items.sort(key=lambda e:e[1])
    item_articles_grouped=[(item,list(items_arts)) for item,items_arts in itertools.groupby(articles_items,key=lambda e:e[1])]
    del articles_items
    # filtering by occ
    items_occs=dict((item,len(items_arts)) for item,items_arts in item_articles_grouped if len(items_arts)>=CONFIG["spans"][span][items_name]["occ"])
    article_items = [t for _ in (items_arts for item,items_arts in item_articles_grouped if len(items_arts)>=CONFIG["spans"][span][items_name]["occ"]) for t in _]
    log("filtered %s by occ>=%s"%(items_name,CONFIG["spans"][span][items_name]["occ"]))
    del item_articles_grouped 

    # grouping by article
    article_items.sort(key=lambda e:e[0])
    article_items = dict((a,list(s for _,s in a_s )) for (a,a_s) in itertools.groupby(article_items,key=lambda e:e[0]) )
    log("%s grouped by articles"%items_name)

    for r,r_as in references_article_grouped:
        # print r_as
        items = [s for ss in (article_items[a] for a,_ in r_as if a in article_items) for s in ss]
        items.sort()
        
        items_grouped=((s, len(list(vs))) for s,vs in itertools.groupby(items))

        items_filtered=[(s,nb) for s,nb in items_grouped if nb>=CONFIG["spans"][span][items_name]["weight"]]
        del items
        del items_grouped

        if len(items_filtered)>0:

            for s,w in items_filtered:
                g.add_node(s,label=s,type=items_name,occurence_count=items_occs[s])
                add_edge_weight(g,r,s,w)
        del items_filtered

    
    log("remove nodes with degree = 0")
    g.remove_nodes_from(r for (r,d) in g.degree_iter() if d <1)
    nb_items_added=len(g.nodes())-nb_nodes_before
    log("added %s %s nodes in network"%(nb_items_added,items_name))
    return nb_items_added 

def process_span(span,span_done,log_messages):    
    
    def log(m):
        if CONFIG["process_verbose"] or CONFIG["report_verbose"] :
            log_messages.put("%s: %s"%(span,m))

    # data to be reported after processing
    span_info={"span":span}
    log("starting")

    g=networkx.Graph()
    if CONFIG["export_ref_format"] =="gexf":
        if CONFIG["process_verbose"] : log("read gexf")
        g=networkx.read_gexf(os.path.join(CONFIG["parsed_data"],span,"%s.gexf"%span),node_type=unicode)
    elif CONFIG["export_ref_format"] == "edgelist":
        if CONFIG["process_verbose"] : log("read csv export")
        g=networkx.read_weighted_edgelist(os.path.join(CONFIG["parsed_data"],span,"%s.csv"%span),delimiter="\t")
    elif CONFIG["export_ref_format"] == "pajek":
        if CONFIG["process_verbose"] : log("read pajek export")
        g=networkx.read_pajek(os.path.join(CONFIG["parsed_data"],span,"%s.csv"%span))
    elif CONFIG["export_ref_format"] == "json":
        if CONFIG["process_verbose"] : log("read pajek export")
        data=json.load(open(os.path.join(CONFIG["parsed_data"],span,"%s.json"%span),"r"),encoding="UTF-8")
        g=json_graph.node_link_graph(data)
    else:
        log("no export compatible export format specified")
        exit(1)

    network_references=g.nodes()
    nb_network_references=len(network_references)

    log("loaded %s ref from graph"%nb_network_references)
    span_info["references_occ_filtered"]=nb_network_references

    with codecs.open(os.path.join(CONFIG["parsed_data"],span,"references.dat"),"r",encoding="UTF-8") as file:
        # dat file have one trailing blank line at end of file
        data_lines=file.read().split("\n")[:-1]
    references_by_articles = [(l.split("\t")[0],",".join(l.split("\t")[1:])) for l in data_lines]
    #references_by_articles_filtered=[(a,r) for a,r in references_by_articles if r in references] 

    references_by_articles.sort(key=lambda e:e[1])
    article_groupby_reference=[(reference,list(ref_arts)) for reference,ref_arts in itertools.groupby(references_by_articles,key=lambda e:e[1])]
    span_info["nb_reference_before_filtering"]=len(article_groupby_reference)
    references_article_grouped=[t for t in article_groupby_reference if len(t[1])>=CONFIG["spans"][span]["references"]["occ"]]
    del article_groupby_reference
    del references_by_articles
    #make sure we have same references than network
    ref_filtered=[r for r,_ in references_article_grouped]
    if(len(ref_filtered))!=nb_network_references:
        s1=set(ref_filtered)
        s2=set(network_references)
        to_remove = s1 - s2
        if len(to_remove)>0:
            log("filtering ref which are not in original network : removing %s ref"%len(to_remove))
            references_article_grouped=[ (r,ref_arts) for r,ref_arts in references_article_grouped if r not in to_remove]
        del s1
        del s2
    del ref_filtered
    del network_references
    # print references_article_grouped
    log("imported, filtered and grouped references by articles")

    span_info["subjects_occ_filtered"]=add_annotations("subjects",references_article_grouped,g,log)
    span_info["authors_occ_filtered"]=add_annotations("authors",references_article_grouped,g,log)
    span_info["institutions_occ_filtered"]=add_annotations("institutions",references_article_grouped,g,log)
    span_info["keywords_occ_filtered"]=add_annotations("keywords",references_article_grouped,g,log)
    span_info["countries_occ_filtered"]=add_annotations("countries",references_article_grouped,g,log)
    
    del references_article_grouped
    
    log("have now %s nodes"%len(g.nodes()))

    if CONFIG["export_ref_annotated_format"] =="gexf":
        log("write gexf export")
        networkx.write_gexf(g,os.path.join(CONFIG["parsed_data"],span,"%s_annotated.gexf"%span))
    elif CONFIG["export_ref_annotated_format"] == "edgelist":
        log("write csv export")
        networkx.write_weighted_edgelist(g,os.path.join(CONFIG["parsed_data"],span,"%s_annotated.csv"%span),delimiter="\t")
    elif CONFIG["export_ref_annotated_format"] == "pajek":
        log("write pajek export")
        networkx.write_pajek(g,os.path.join(CONFIG["parsed_data"],span,"%s_annotated.net"%span))
    elif CONFIG["export_ref_annotated_format"] == "graphml":
        log("write pajek export")
        networkx.write_graphml(g,os.path.join(CONFIG["parsed_data"],span,"%s_annotated.graphml"%span))
    else:
        log("no compatible export format specified")

    with codecs.open(os.path.join(CONFIG["parsed_data"],span,"articles.dat"),"r",encoding="UTF-8") as articles_file:
        nb_articles=len(articles_file.read().split("\n")[:-1])
    
    span_info["nb_articles"]=nb_articles    
    span_done.put(span_info)
    del g

def logger(filename,log_messages):
    while True:
        m=log_messages.get()
        with open(filename,"a") as logfile:
            logfile.write(m+"\n")
            logfile.flush()
        log_messages.task_done() 


def write_to_csv(lines):
    with open(os.path.join(CONFIG["reports_directory"],"filtering_report.csv"),"a") as csvfile:
        csvfile.write("\n"+"\n".join(lines))
        csvfile.flush()
  

#############################################################################

span_done = JoinableQueue()
log_messages = JoinableQueue()


spans_to_process=sorted(CONFIG["spans"],reverse=True)

# prepare csv report
if CONFIG["report_csv"]:
    if os.path.exists(os.path.join(CONFIG["reports_directory"],"filtering_report.csv")):
        os.remove(os.path.join(CONFIG["reports_directory"],"filtering_report.csv"))
    line=["span","nb articles","nb ref","f_ref","nb_ref_filtered","ratio_prev_ref"]
    for items in ["subjects","authors","institutions","keywords","countries"]:
            line+=["f %s"%items,"nb %s"%items,"p %s"%items]
    csv_export=[]
    csv_export.append(",".join(line))
    write_to_csv(csv_export)

# create the logger process
log_filename="annotated_network_processing.log"
if os.path.exists(log_filename):
    os.remove(log_filename)
logger = Process(target=logger, args=(log_filename,log_messages))
logger.daemon = True
logger.start()

# create the first process on spans
span_procs={}
for _ in range(min(CONFIG["nb_processes"],len(spans_to_process))):
    span=spans_to_process.pop()
    p = Process(target=process_span, args=(span,span_done,log_messages))
    p.daemon = True
    p.start()
    span_procs[span]=p


while len(spans_to_process)>0 or len(span_procs)>0:
    s=span_done.get()
    span_procs[s["span"]].join()
    log_messages.put("%s done"%s['span'])
    del span_procs[s["span"]]

    # create a new process if needed
    print "still %s spans to process"%len(spans_to_process)
    if len(spans_to_process)>0:
        next_span=spans_to_process.pop()
        span_procs[next_span]=Process(target=process_span, args=(next_span,span_done,log_messages))
        span_procs[next_span].daemon = True
        span_procs[next_span].start()
        print "new process on %s"%next_span
    # write csv
    if CONFIG["report_csv"]:
        csv_export=[]
        line=[s["span"]]
        line.append(s["nb_articles"])
        nb_reference_before_filtering=s["nb_reference_before_filtering"]
        line.append(nb_reference_before_filtering)
        line.append("%s | %s"%(CONFIG["spans"][span]["references"]["occ"],CONFIG["spans"][span]["references"]["weight"]))
        nb_ref_filtered=s["references_occ_filtered"]
        line.append(nb_ref_filtered)
        line.append("%04.1f"%(float(nb_reference_before_filtering)/int(csv_export[-1].split(",")[2])) if len(csv_export)>1 else "")
        for items in ["subjects","authors","institutions","keywords","countries"]:
            f=CONFIG["spans"][span][items]["weight"]
            nb=s["%s_occ_filtered"%items]
            p="%04.1f | %04.1f"%(float(nb)/nb_reference_before_filtering*1000,float(nb)/s['nb_articles']*1000)
            line+=[f,nb,p]
        csv_export.append(",".join(str(_) for _ in line))
        write_to_csv(csv_export)

    span_done.task_done()

# c'est fini !
span_done.join()
log_messages.join()
logger.terminate()




