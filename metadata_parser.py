import importlib
import importlib.metadata
import requests
from metadata_validator import MetadataAnalyzer
from bs4 import BeautifulSoup
import gem
import subprocess

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

class MetadataParser:
	def __init__(self,package_name,repo="PYTHON_REPO"):
		if repo == 'PYTHON_REPO':
			self.repo = repo_list[repo]+package_name+"/json"
		elif repo == 'GEMS_REPO':
			self.repo = repo_list[repo]+package_name+".json"
		else:
			self.repo = repo_list[repo]+package_name
	
	
	def FetchPackageMetadata(self):
		url = self.repo
		response = requests.get(url)
		if response.status_code == 200:
			return response.json()
		else:
			return None
		
	def ParsePackageMetadata(self):
		return "Hello World"


'''
CHECK AND FETCH LOCAL PACKAGE METADATA
'''
class LocalMetadataInfo:
	def __init__(self,repo="PYTHON_REPO"):
		self.repo = repo
	
	def IsPythonPackageInstalled(self,package_name):
		try:
			importlib.import_module(package_name)
			return True
		except ModuleNotFoundError:
			return False
	
	def IsNpmPackageInstalled(self,package_name):
		command = ["npm", "list", "-g", package_name]
		output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if output.returncode == 0:
			return True
		else:
			return False

	def IsRubyPackageInstalled(self, package_name):
		command = ["gem", "list", "-i", package_name]
		output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if output.returncode == 0:
			return True
		else:
			return False
			
	def IsPackageInstalled(self,package_name):
		if self.repo == "PYTHON_REPO":
			return self.IsPythonPackageInstalled(package_name)
		elif self.repo == "NPM_REPO":
			return self.IsNpmPackageInstalled(package_name)
		else:
			return self.IsRubyPackageInstalled(package_name)

'''
DRIVER RELEASED TO CLIENT
'''

class MetadataInfo:
	def FetchAndParse(package_name,repo):
		md_parser = MetadataParser(package_name,repo)
		return md_parser.FetchPackageMetadata()
	
	def IsPackageInstalled(package_name,repo):
		b_md_info = LocalMetadataInfo(repo)
		return b_md_info.IsPackageInstalled(package_name)
