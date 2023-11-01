import importlib
import importlib.metadata
import requests
import json
import os
import sys
from bs4 import BeautifulSoup
from MetadataAnalyzer import MetadataAnalyzer
from ParseUtil import Parser


repo_list = {
1: 'GEMS_REPO',
2: 'NPM_REPO',
3: 'PYTHON_REPO'
}

if __name__ == "__main__":
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print("Unable to find the file, please retry..")
        exit(1)
    '''
    print('The following packages are supported for analysis...')
    print('1. Gems Package')
    print('2. NPM Package')
    print('3. Python Package')
    '''
    
    repo = int(sys.argv[2])
    
    if repo == 1:
    	print('Initializing Gems Analyzer...\n')
    elif repo == 2:
    	print('Initializing NPM Analyzer...\n')
    elif repo == 3:
    	print('Initializing Python Analyzer...\n')
    else:
    	print('Invalid selection, try again...\n')
    	exit(1)
    
    with open(file_path,"r") as f:
    	packages = f.readlines()
    
    for package in packages:
        package_name = package.replace('\n','')
        print(f'Analyzing package : {package_name}')
        parser = Parser(package_name,repo_list[repo])
        remote_pkg_metadata = parser.FetchAndParseRemote()
        local_pkg_metadata = parser.FetchAndParseLocal()
        print('Analyzing package for issues related to metadata\n\n')
        '''with open('npm_remote_md','w') as f:
            json.dump(remote_pkg_metadata,f,indent=4)
        
        with open('npm_local_md','w') as f:
            json.dump(local_pkg_metadata,f,indent=4)
        
        break'''
        b_metadata_analysis_res = ''

        if local_pkg_metadata:
            b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,local_pkg_metadata,repo)
        else:
            b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,None,repo)
        
        print(b_metadata_analysis_res)
        print('\n')
