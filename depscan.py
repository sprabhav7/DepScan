import importlib
import importlib.metadata
import requests
import json
import os
import sys
from bs4 import BeautifulSoup
from MetadataAnalyzer import MetadataAnalyzer
from ParseUtil import Parser
from AttackAnalyzer import AttackAnalyzer


def usage():
	print('USAGE\npython3 depscan.py <VALUE> <FILE NAME> <OPTIONAL ARGS> <REPORT FILE>')
	print('\nVALUE')
	print('1	GEMS Packages')
	print('2	NPM Packages')
	print('3	PYTHON Packages')
	print('\nOPTIONAL ARGS')
	print('-a	run all attack analysis checks')
	print('-d	run dependency confusion analysis checks')
	print('-t	run typosquatting analysis checks')
	print('\nREPORT FILE')
	print('Analyzer output is written to a report file with name REPORT_FILE. If nothing is provided, will be return to console.')
	exit(0)

if __name__ == "__main__":
    
    inp_len = len(sys.argv)
    if inp_len <= 2 or inp_len >= 6:
        usage()
    
    repo = int(sys.argv[1])
    file_path = sys.argv[2]
    
    if not os.path.exists(file_path):
        print("Unable to find the file, please retry..")
        exit(1)
    
    if repo not in range(1,4):
        usage()
    
    if inp_len == 4:
        opt_args = sys.argv[3]
        if opt_args not in ['-t','-d','-a']:
            usage()
    else:
        opt_args = '-a'
	
    if inp_len == 5:
        out_file = sys.argv[4]
    else:
        out_file = None
    
    if repo == 1:
    	print('INFO: Initializing Gems Analyzer...')
    elif repo == 2:
    	print('INFO: Initializing NPM Analyzer...')
    elif repo == 3:
    	print('INFO: Initializing Python Analyzer...')
    else:
    	print('ERROR: Invalid selection, try again...')
    	exit(1)
    	
    with open(file_path,"r") as f:
    	packages = f.readlines()
    
    b_analysis_res = dict()
    
    for package in packages:
        package_name = package.replace('\n','')
        print(f'\nINFO: Analyzing package : {package_name}')
        parser = Parser(package_name,repo)
        remote_pkg_metadata = parser.FetchAndParseRemote()
        local_pkg_metadata = parser.FetchAndParseLocal()
        
        b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,local_pkg_metadata,repo)
        b_attack_analysis_res = AttackAnalyzer(remote_pkg_metadata,repo,opt_args).Analyzer()
        
        b_analysis_res[package_name] = b_metadata_analysis_res
        b_analysis_res[package_name].update(b_attack_analysis_res)
        
    
    print('\nINFO: Report has been generated\n')
    if out_file is None:
        print(json.dumps(b_analysis_res,indent=4))
    else:
        with open(out_file, 'w') as f:
            json.dump(b_analysis_res, f, indent=4)
