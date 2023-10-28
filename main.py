import importlib
import importlib.metadata
import requests
from bs4 import BeautifulSoup
from metadata_validator import MetadataAnalyzer
from metadata_parser import Parser


repo_list = {
1: 'GEMS_REPO',
2: 'NPM_REPO',
3: 'PYTHON_REPO'
}

if __name__ == "__main__":
    # TODO - Parse file, get repo type
    print('The following packages are supported for analysis...')
    print('1. Gems Package')
    print('2. NPM Package')
    print('3. Python Package')
    
    repo = int(input("Enter the number for the relevant package:"))
    package_name = input("Enter the package name: ")
    
    parser = Parser(package_name,repo_list[repo])
    remote_pkg_metadata = parser.FetchAndParseRemote()
    local_pkg_metadata = parser.FetchAndParseLocal()
    print(local_pkg_metadata)	    
    exit(1)
    b_metadata_analysis_res = ''
    attack_analysis_res = ''
    # call metadata analysis here
    b_metadata_analysis_res = MetadataAnalyzer.MetadataAnalyzer(remote_pkg_metadata,local_pkg_metadata,repo)
    for key,value in b_metadata_analysis_res.items():
        if value is False:
            print(f'Mismatch between local {key} and remote {key} metadata fields')
    
    print('Passed metadata check')
    exit(1)
    if Parser.IsPackageInstalled(package_name,repo):
        local_pkg_metadata = 'get and parse local metadata'
        print("Successfully fetched local copy and remote copy...")
        exit(1)
        # call attack analysis with context_metadata
    else:
        print(f"The package {package_name} is not installed. Reverting back to popularity metrics...")
        # call attack analysis with nonetype
        #res = analyze_package_metadata(metadata, "Python")
        #print(res)
        exit(1)
