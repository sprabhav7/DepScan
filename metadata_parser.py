import importlib
import importlib.metadata
import requests
import json
from metadata_validator import MetadataAnalyzer
from bs4 import BeautifulSoup
import gem
import subprocess
import os
import re
import yaml
import pkg_resources
from collections.abc import Iterable

'''
PUBLIC REPO LIST
'''

repo_list = {
'PYTHON_REPO': 'https://pypi.org/pypi/',
'NPM_REPO': 'https://registry.npmjs.org/',
'GEMS_REPO': 'https://rubygems.org/api/v1/gems/'
}


'''
FETCH AND PARSE METADATA FROM PUBLIC REPO
'''

class ParseMetadata:
	def __init__(self,repo):
		self.repo = repo
	
		
	def ParseMetadata(self, metadata,location):
		if self.repo == 'PYTHON_REPO':
			return self.ParsePythonPackageMetadata(metadata,location)
		elif self.repo == 'NPM_REPO':
			return self.ParseNpmPackageMetadata(metadata,location)
		else:
			return 'Hello World'
			
	def ParsePythonPackageMetadata(self,metadata,location):
		parsed_metadata = {}
		if metadata:
			if location == 'remote':
				parsed_metadata['name'] = metadata['info']['name']
				parsed_metadata['version'] = metadata['info']['version']
				parsed_metadata['summary'] = metadata['info']['summary']
				parsed_metadata['author'] = metadata['info']['author']
				parsed_metadata['maintainer'] = metadata['info']['maintainer']
				parsed_metadata['license'] = metadata['info']['license']
				parsed_metadata['project-url']= metadata['info']['home_page']
				parsed_metadata['dependencies'] = metadata['info']['requires_dist']
			
			else:
				parsed_metadata['name'] = metadata['name']
				parsed_metadata['version'] = metadata['version']
				parsed_metadata['summary'] = metadata['summary']
				parsed_metadata['author'] = metadata['author']
				parsed_metadata['maintainer'] = metadata['maintainer']
				parsed_metadata['license'] = metadata['license']
				parsed_metadata['project-url']= metadata['home-page']
				parsed_metadata['dependencies'] = metadata['requires-dist']
				parsed_metadata['python-specific'] = {}
		
		return parsed_metadata
	
	def ParseNpmPackageMetadata(self,metadata,location):
		
		parsed_metadata = {}
		parsed_metadata['name'] = metadata['name'] if 'name' in metadata.keys() else None
		parsed_metadata['version'] = metadata['version'] if 'version' in metadata.keys() else None
		parsed_metadata['summary'] = metadata['description'] if 'description' in metadata.keys() else None
		parsed_metadata['maintainer'] = metadata['maintainers'] if 'maintainers' in metadata.keys() else None
		parsed_metadata['license'] = metadata['license'] if 'license' in metadata.keys() else None
		parsed_metadata['author'] = metadata['author'] if 'author' in metadata.keys() else None
		parsed_metadata['project-url']= metadata['homepage'] if 'homepage' in metadata.keys() else None
		parsed_metadata['dependencies'] = metadata['dependencies'] if 'dependencies' in metadata.keys() else None
		parsed_metadata['versions'] = metadata['versions'] if 'versions' in metadata.keys() else None
		return parsed_metadata
			

'''
CHECK AND FETCH LOCAL PACKAGE METADATA
'''

class FetchMetadata:
	def __init__(self,package_name,repo):
		self.package_name = package_name
		self.repo = repo
		if repo == 'PYTHON_REPO':
			self.url = repo_list[repo]+package_name+"/json"
		elif repo == 'GEMS_REPO':
			self.url = repo_list[repo]+package_name+".json"
		else:
			self.url = repo_list[repo]+package_name+"/latest"
	
	def IsPythonPackageInstalled(self,package_name):
		try:
			metadata = importlib.metadata.metadata(package_name)
			return metadata

		except ModuleNotFoundError:
			return None
	
	def IsNpmPackageInstalled(self,package_name):
		command = ["npm", "view", "-g", package_name, "--json"]
		output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if output.returncode == 0:
			return json.loads(output.stdout.decode())
		else:
			return None
		
		
	def FetchLocalMetadata(self):
		if self.repo == 'PYTHON_REPO':
			return self.IsPythonPackageInstalled(self.package_name)
		elif self.repo == 'NPM_REPO':
			return self.IsNpmPackageInstalled(self.package_name)
		else:
			return 'Hello World'


	def FetchRemoteMetadata(self):
		url = self.url
		response = requests.get(url)
		if response.status_code == 200:
			return json.loads(response.content)
		else:
			return None


'''
DRIVER RELEASED TO CLIENT
'''
class Parser:
	def __init__(self,package_name,repo):
		self.fetcher = FetchMetadata(package_name,repo)
		self.parser = ParseMetadata(repo)
		self.package_name = package_name
	
	def FetchAndParseLocal(self):
		#return self.fetcher.FetchLocalMetadata()
		#return self.parser.ParseMetadata(self.fetcher.FetchLocalMetadata(),'local')
		return pkg_resources.get_distribution(self.package_name)
		
	def FetchAndParseRemote(self):
		#return self.fetcher.FetchRemoteMetadata()
		return self.parser.ParseMetadata(self.fetcher.FetchRemoteMetadata(),'remote')
		
