import importlib
import importlib.metadata
import requests
import json
import os
from bs4 import BeautifulSoup
from MetadataAnalyzer import MetadataAnalyzer
from ParseUtil import Parser


repo_list = {
1: 'GEMS_REPO',
2: 'NPM_REPO',
3: 'PYTHON_REPO'
}

if __name__ == "__main__":
    
    file_path = input("Enter the absolute path to the packages file:\n")
    
    if not os.path.exists(file_path):
        print("Unable to find the file, please retry..")
        exit(1)
    
    print('The following packages are supported for analysis...')
    print('1. Gems Package')
    print('2. NPM Package')
    print('3. Python Package')
    
    repo = int(input("Enter the number for the relevant packge for analysis:"))
    
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
            for item in list(remote_pkg_metadata.keys()):
            	f.write(item+'\n')
        
        with open('npm_local_md','w') as f:
            for item in list(local_pkg_metadata.keys()):
            	f.write(item+'\n')
        
        break'''
        b_metadata_analysis_res = ''

        if local_pkg_metadata:
            b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,local_pkg_metadata,repo)
        else:
            b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,None,repo)
        
        print(json.dumps(b_metadata_analysis_res))
