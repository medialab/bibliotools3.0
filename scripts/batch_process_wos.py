from co2_links import prep_het_graph
from parser import Wos_parser
import os
import datetime
from multiprocessing import Pool

#wos exports grouped in subfolders
indir="/store/bibtools-data-utf8"
outdir_prefix= "/store/bibtools-results/large2_%s"%datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def process_wos(subfolder):
	years=os.path.split(subfolder)[-1]

	os.mkdir(os.path.join(outdir_prefix,years))
	#parser output
	parsed_folder=os.path.join(outdir_prefix,years,"parsed")
	os.mkdir(parsed_folder)
	#network output
	network_folder=os.path.join(outdir_prefix,years,"networks")
	os.mkdir(network_folder)
	print "%s : directories created, start parsing"%years
	Wos_parser(subfolder,parsed_folder,True)
	print "%s : parsing done, start networks gen"%years
	small_thresholds={"l_thr":1,"vA":111111111,"vK":14,"vS":2,"vR":4,"vTK":20,"vY":11111111,"vC":3,"vJ":1111111,"vI":111111,"vRJ":111111111111}
	medium_thresholds={"l_thr":2,"vA":111111111,"vK":28,"vS":4,"vR":12,"vTK":40,"vY":11111111,"vC":6,"vJ":1111111,"vI":111111,"vRJ":111111111111}
	large_thresholds={"l_thr":3,"vA":111111111,"vK":56,"vS":8,"vR":36,"vTK":80,"vY":11111111,"vC":12,"vJ":1111111,"vI":111111,"vRJ":111111111111}
	medium2_thresholds={"l_thr":2,"vA":111111111,"vK":21,"vS":3,"vR":8,"vTK":30,"vY":11111111,"vC":4,"vJ":1111111,"vI":111111,"vRJ":111111111111}
	large2_thresholds={"l_thr":3,"vA":111111111,"vK":56,"vS":8,"vR":24,"vTK":80,"vY":11111111,"vC":12,"vJ":1111111,"vI":111111,"vRJ":111111111111}
	prep_het_graph(parsed_folder,network_folder,0,True,large2_thresholds)
	print "%s : network gen done, exit"%years
	return True


os.mkdir(outdir_prefix)
subfolders=os.listdir(indir)

#pool = Pool(processes=2)

for subfolder in sorted(subfolders):
	print subfolder
 	process_wos(os.path.join(indir,subfolder),)
#pool.close()
#pool.join()
