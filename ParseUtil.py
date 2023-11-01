import importlib
import importlib.metadata
import requests
import json
from MetadataAnalyzer import MetadataAnalyzer
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


class ParseMetadata:
	def __init__(self,repo):
		self.repo = repo
	
		
	def ParseMetadata(self, metadata,location):
		if self.repo == 'PYTHON_REPO':
			return self.ParsePythonPackageMetadata(metadata,location)
		elif self.repo == 'NPM_REPO':
			return self.ParseNpmPackageMetadata(metadata,location)
		else:
			return self.ParseRubyPackageMetadata(metadata,location)
			
	def ParsePythonPackageMetadata(self,metadata,location):
		if metadata is None:
			return None
		parsed_metadata = {}
		if metadata:
			if location == 'remote':
				parsed_metadata['name'] = metadata['info']['name'] if 'name' in metadata['info'].keys() else None
				parsed_metadata['version'] = metadata['info']['version'] if 'version' in metadata['info'].keys() else None
				parsed_metadata['summary'] = metadata['info']['summary'] if 'summary' in metadata['info'].keys() else None
				parsed_metadata['author'] = metadata['info']['author'] if 'author' in metadata['info'].keys() else None
				parsed_metadata['author-email'] = metadata['info']['author_email'] if 'author_email' in metadata['info'].keys() else None
				parsed_metadata['maintainer'] = metadata['info']['maintainer'] if 'maintainer' in metadata['info'].keys() else None
				parsed_metadata['maintainer-email'] = metadata['info']['maintainer_email'] if 'maintainer_email' in metadata['info'].keys() else None
				parsed_metadata['license'] = metadata['info']['license'] if 'license' in metadata['info'].keys() else None
				parsed_metadata['project-url']= metadata['info']['home_page'] if 'home_page' in metadata['info'].keys() else None
				parsed_metadata['dependencies'] = metadata['info']['requires_dist'] if 'requires_dist' in metadata['info'].keys() else None
				parsed_metadata['versions'] = metadata['releases'] if 'releases' in metadata.keys() else None
			
			else:
				parsed_metadata['name'] = metadata['name'] if 'Name' in metadata.keys() else None
				parsed_metadata['version'] = metadata['version'] if 'Version' in metadata.keys() else None
				parsed_metadata['summary'] = metadata['summary'] if 'Summary' in metadata.keys() else None
				parsed_metadata['author'] = metadata['author'] if 'Author' in metadata.keys() else None
				parsed_metadata['maintainer'] = metadata['maintainer'] if 'Maintainer' in metadata.keys() else None
				parsed_metadata['author-email'] = metadata['author-email'] if 'Author-email' in metadata.keys() else None
				parsed_metadata['maintainer-email'] = metadata['maintainer-email'] if 'Maintainer-email' in metadata.keys() else None
				parsed_metadata['license'] = metadata['license'] if 'License' in metadata.keys() else None
				parsed_metadata['project-url']= metadata['home-page'] if 'Home-page' in metadata.keys() else None
				parsed_metadata['dependencies'] = metadata['requires-dist'] if 'Requires-Dist' in metadata.keys() else None
			
		for key,value in parsed_metadata.items():
			if value == '':
				parsed_metadata[key] = None
		
		
		return parsed_metadata
	
	def ParseNpmPackageMetadata(self,metadata,location):
		if metadata is None:
			return None
		parsed_metadata = {}
		parsed_metadata['name'] = metadata['name'] if 'name' in metadata.keys() else None
		parsed_metadata['version'] = metadata['version'] if 'version' in metadata.keys() else None
		parsed_metadata['summary'] = metadata['description'] if 'description' in metadata.keys() else None
		parsed_metadata['maintainer'] = metadata['maintainers'] if 'maintainers' in metadata.keys() else None
		parsed_metadata['license'] = metadata['license'] if 'license' in metadata.keys() else None
		parsed_metadata['author'] = metadata['author'] if 'author' in metadata.keys() else None
		parsed_metadata['project-url']= metadata['homepage'] if 'homepage' in metadata.keys() else None
		parsed_metadata['dependencies'] = metadata['dependencies'] if 'dependencies' in metadata.keys() else None
		parsed_metadata['time'] = metadata['time'] if 'time' in metadata.keys() else None
		parsed_metadata['keywords'] = metadata['keywords'] if 'keywords' in metadata.keys() else None
		parsed_metadata['downloads'] = metadata['downloads'] if 'downloads' in metadata.keys() else None
		if location == 'remote':
			parsed_metadata['versions'] = metadata['versions'] if 'versions' in metadata.keys() else None
			command = ["npm", "show", "-g", metadata['name'] , "--json"]
			output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			if output.returncode == 0:
				met_data = json.loads(output.stdout.decode())
				parsed_metadata['version'] = met_data['version'] 
				parsed_metadata['dependencies'] = met_data['dependencies'] if 'dependencies' in met_data.keys() else None
		return parsed_metadata
	
	def ParseRubyPackageMetadata(self,metadata,location):
		if metadata is None:
			return None
		parsed_metadata = {}
		parsed_metadata['name'] = metadata['name'] if 'name' in metadata.keys() else None
		parsed_metadata['version'] = metadata['version'] if 'version' in metadata.keys() else None
		parsed_metadata['license'] = metadata['licenses'] if 'licenses' in metadata.keys() else None
		parsed_metadata['author'] = metadata['authors'] if 'authors' in metadata.keys() else None
		parsed_metadata['metadata'] = metadata['metadata'] if 'metadata' in metadata.keys() else None
		parsed_metadata['dependencies'] = metadata['dependencies'] if 'dependencies' in metadata.keys() else None
		
		if location == 'remote':
			parsed_metadata['summary'] = metadata['info'] if 'info' in metadata.keys() else None
			parsed_metadata['project-url']= metadata['homepage_uri'] if 'homepage_uri' in metadata.keys() else None
			parsed_metadata['time'] = metadata['version_created_at'].split('T')[0] if 'time' in metadata.keys() else None
			parsed_metadata['downloads'] = metadata['downloads'] if 'downloads' in metadata.keys() else None
		else:
			parsed_metadata['summary'] = metadata['description'] if 'description' in metadata.keys() else None
			parsed_metadata['project-url']= metadata['homepage'] if 'homepage' in metadata.keys() else None
			parsed_metadata['time'] = metadata['date'].split('T')[0] if 'date' in metadata.keys() else None
								
		
		return parsed_metadata
		
		
class FetchMetadata:
	def __init__(self,package_name,repo):
		self.package_name = package_name
		self.repo = repo
		if repo == 'PYTHON_REPO':
			self.url = repo_list[repo]+package_name+"/json"
		elif repo == 'GEMS_REPO':
			self.url = repo_list[repo]+package_name+".json"
		else:
			self.url = repo_list[repo]+package_name
	
	def IsPythonPackageInstalled(self,package_name):
		try:
			metadata = importlib.metadata.metadata(package_name)
			return metadata

		except ModuleNotFoundError:
			return None
			
	def IsRubyPackageInstalled(self,package_name):
		try:
			command = ["gem", "specification", package_name]
			output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
			
			for s in re.findall(r'--- !ruby[^ ]+\n',output): output = output.replace(s,'---\n')
			for s in re.findall(r': !ruby[^ ]+\n',output): output = output.replace(s,':\n')
			for s in re.findall(r'- !ruby[^ ]+\n[ ]+',output): output = output.replace(s,'- ')
			
			output = yaml.safe_load(output)
			output['date'] = output['date'].strftime("%Y-%m-%dT%H:%M:%S")
			return output
		except subprocess.CalledProcessError as e:
			return None
	
	def IsNpmPackageInstalled(self,package_name):
		path = f'/usr/local/lib/node_modules/{package_name}/package.json'
		if os.path.exists(path):
			with open(path,'r') as f:
				return json.load(f)
		else:
			return None
		
		
	def FetchLocalMetadata(self):
		if self.repo == 'PYTHON_REPO':
			return self.IsPythonPackageInstalled(self.package_name)
		elif self.repo == 'NPM_REPO':
			return self.IsNpmPackageInstalled(self.package_name)
		else:
			return self.IsRubyPackageInstalled(self.package_name)


	def FetchRemoteMetadata(self):
		url = self.url
		response = requests.get(url)
		if response.status_code == 200:
			return json.loads(response.content.decode())
		else:
			return None


class Parser:
	def __init__(self,package_name,repo):
		self.fetcher = FetchMetadata(package_name,repo)
		self.parser = ParseMetadata(repo)
		self.package_name = package_name
	
	def FetchAndParseLocal(self):
		#return self.fetcher.FetchLocalMetadata()
		return self.parser.ParseMetadata(self.fetcher.FetchLocalMetadata(),'local')
		
	def FetchAndParseRemote(self):
		#return self.fetcher.FetchRemoteMetadata()
		return self.parser.ParseMetadata(self.fetcher.FetchRemoteMetadata(),'remote')
		
