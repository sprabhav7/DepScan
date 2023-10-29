import importlib
import importlib.metadata
import requests
import json
from bs4 import BeautifulSoup
from MetadataAnalyzer import MetadataAnalyzer
from ParseUtil import Parser


repo_list = {
1: 'GEMS_REPO',
2: 'NPM_REPO',
3: 'PYTHON_REPO'
}

if __name__ == "__main__":
    
    print('The following packages are supported for analysis...')
    print('1. Gems Package')
    print('2. NPM Package')
    print('3. Python Package')
    
    repo = int(input("Enter the number for the relevant package:"))
    package_name = input("Enter the package name: ")
    
    parser = Parser(package_name,repo_list[repo])
    remote_pkg_metadata = parser.FetchAndParseRemote()
    local_pkg_metadata = parser.FetchAndParseLocal()
    
    b_metadata_analysis_res = ''
    attack_analysis_res = ''
    
    if local_pkg_metadata:
        print("Successfully fetched local copy and remote copy...")
        b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,local_pkg_metadata,repo)
        print(b_metadata_analysis_res)
        # call attack analysis with context_metadata
        
    else:
        print(f"The package {package_name} is not installed. Reverting back to online popularity metrics...")
        b_metadata_analysis_res = MetadataAnalyzer.Analyzer(remote_pkg_metadata,None,repo)
        print(b_metadata_analysis_res)
        # call attack analysis with nonetype
        exit(1)
