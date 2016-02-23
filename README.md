bibliotools3.0
==============

Paul Girard added an alternative set of scripts to build the references cooccurences network.
It follows this methodological chain:

#### 0. download WOS data
download a set of WOS exports files in full format

#### 1. Merge all files in one 
```bash
$python merging_corpus.py
```
This will output one file with all wos records inside and a years_distribution.csv counting articles by year.
While doing the merge the script checks some data formats known issues.
Edit mergin_corpus.py to add some more premilinary cleaning.

#### 1-2. Define the time-spans
The years_distribution.csv (in reports_directory) will help you to decide how you will cut your corpus in time spans.
To do so edt config.py to add spans.

#### 2. Group files by time-span and parse them
```bash
$python parse_and_group.py
```
This will split the corpus into time-spans writing one file for each in a specific folder.
It will then parse the many WOS files to outputs article-id{tab}items indeces files.
Items are : references, subjects, authors, institutions, keywords, countries.

This steps uses parser.py and Utils.py from bibliotools 2. You'll find in this repository a better version of parser.py  and Utils.py in which I removed [one important bug](https://github.com/medialab/bibliotools3.0/commit/38bd140af4f0246930e730a47ad3ef5027c63b3c).

#### 2-3. Define filtering
```bash
$python corpus_parsed_overview.py
```
Which will output many reports about the corpus.

Open "name"_references_distribution.csv in the folder reports
Check the number of occurrence (first column) when the cumulative % of reference (third column) becomes significantly higher 
--> This gives you an idea of the minimum number of occurrence to filter your data in order to get a readable graph
ADD DOCUMENTATION about the reports

#### 3. generate REF-REF cooccurrence network
```bash
$python filter_and_network_ref.py
```
This script will filter references on occurences number and then generate the RE-REF network adding and edge whose weight is the number of articles co-citing those 2 references.
The scripts filters edges on weight as defined in config.py.
The script will output one network file "span-name.gexf" by time-span in format specified in config.py.

#### 4. add items nodes and edges
```bash
$python annotations_multiproc.py
```
This script will add items nodes and edges between ref and items.
It will filters as previous steps on occurences and edge weight.

This script outputs a report which can help defining the weight filtering.

ADD DOCUMENTATION about this reports and how to use

This script output one network "span-name_annotated.graphml" by time-span.

#### 5. analyse the networks
The method proposed to analyse those networks consists in spacializing the ref-ref network only.
Then to settle this ref-ref network as the basemap.
Then one can add one or more layer(s) of annotation as ref-item edges and spacialize the items over the ref-ref basemap.

To do so in [Gephi](http://www.gephi.org):
- open a span-name_annotated.graphml graph
- filter on type node attribute to keep references only
- spacialize using one layout (we love [ForceAtlas 2](http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0098679))
- in filter, select the references only
- right-click and choose settle in context-menu
- remove your filter
- in Partition, color node on attribute type
- start the layout again to position the items (references, subjects, authors, institutions, keywords, countries)
- Now you can try to understand how your scientific papers corpus is based on references communities and to describe those communities by analysing their use of keywords, subjects...

#### requirements
```
pip install networkx
```	


### this work is a modification of bibliotools 2.2 from Sébastian Grauwin
http://www.sebastian-grauwin.com/?page_id=492

   The BiblioTools are a set of python scripts performing several scientometric analysis on a (WOS) bibligraphic database, among which

   ** Statistical (frequency) analysis of the keywords, subjects, journals of publication, authors, institutions, countries, references.
   ** Possibility to filter your data (in particular the institutions and laboratory names)
   ** Cocitation networks : construction of static or dynamic networks (co-authors, co-citations, heterogeneous networks, ...) with a gephi output. 
   ** Bibliographic Coupling network: construction, detection and detailed caracterisation of the communities.

   More information (tutorials, examples, references...)
   GO TO http://www.sebastian-grauwin.com
