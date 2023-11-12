import importlib
import importlib.metadata
import requests
import json
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
3: 'https://pypi.org/pypi/',
2: 'https://registry.npmjs.org/',
1: 'https://rubygems.org/api/v1/gems/'
}


class ParseMetadata:
	def __init__(self,repo):
		self.repo = repo
	
		
	def ParseMetadata(self, metadata,location):
		if self.repo == 3:
			return self.ParsePythonPackageMetadata(metadata,location)
		elif self.repo == 2:
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
				
				api_url = f'https://pypistats.org/api/packages/{metadata["info"]["name"]}/recent'
				response = requests.get(api_url)
				if response.status_code == 200:
					parsed_metadata['downloads'] = response.json()['data']['last_week']
				else:
					parsed_metadata['downloads'] = 0
				parsed_metadata['age'] = metadata['releases'][metadata['info']['version']][0]['upload_time']
			
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
		parsed_metadata['age'] = metadata['time'] if 'time' in metadata.keys() else None
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
			parsed_metadata['age'] = metadata['version_created_at'].split('.')[0] if 'version_created_at' in metadata.keys() else None
			parsed_metadata['downloads'] = metadata['downloads'] if 'downloads' in metadata.keys() else None
			parsed_metadata['versions'] = self.GetGemVersions(metadata['name'])
		else:
			parsed_metadata['summary'] = metadata['description'] if 'description' in metadata.keys() else None
			parsed_metadata['project-url']= metadata['homepage'] if 'homepage' in metadata.keys() else None
			parsed_metadata['age'] = metadata['date'].split('.')[0] if 'date' in metadata.keys() else None
								
		
		return parsed_metadata
	
	def GetGemVersions(self,package_name):
		url = f"https://rubygems.org/api/v1/versions/{package_name}.json"
		response = requests.get(url)
		
		if response.status_code == 200:
			versions_data = response.json()
			return [version["number"] for version in versions_data]
		else:
			return None
		
class FetchMetadata:
	def __init__(self,package_name,repo):
		if package_name is None:
			return
		self.package_name = package_name
		self.repo = repo
		if repo == 3:
			self.url = repo_list[repo]+package_name+"/json"
		elif repo == 1:
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
		if self.repo == 3:
			return self.IsPythonPackageInstalled(self.package_name)
		elif self.repo == 2:
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
	
	def FetchFromTrusted(self,url):
		response = requests.get(url)
		if response.status_code == 200:
			return json.loads(response.content.decode())
		else:
			return None

	

class Parser:
	def __init__(self,package_name=None,repo=None):
		self.fetcher = FetchMetadata(package_name,repo)
		self.parser = ParseMetadata(repo)
		self.package_name = package_name
	
	def FetchAndParseLocal(self):
		return self.parser.ParseMetadata(self.fetcher.FetchLocalMetadata(),'local')
		
	def FetchAndParseRemote(self):
		return self.parser.ParseMetadata(self.fetcher.FetchRemoteMetadata(),'remote')
		
	def FetchAndParseRemoteTrusted(self,url):
		return self.parser.ParseMetadata(self.fetcher.FetchFromTrusted(url),'remote')
