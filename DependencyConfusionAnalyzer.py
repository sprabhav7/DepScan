import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import pip
import datetime
import logging
from ParseUtil import Parser
from bs4 import BeautifulSoup

safe_repo_list = {
1: 'https://rubygems.org/api/v1/gems/',
2: 'https://registry.npmjs.org/',
3: 'https://pypi.org/pypi/'
}

class DependencyConfusionAnalyzer:
	def __init__(self, remote_metadata,repo):
		print('Starting dependency confusion analyzer\n')
		self.remote_metadata= remote_metadata
		self.trusted_metadata = None
		self.repo = repo
		self.res = {}
		self.security_features = ['version', 'summary', 'author', 'dependencies', 'project-url', 'versions']
		logging.basicConfig(level=logging.DEBUG)
	
	def analyze(self):
		self.FetchFromTrusted()
		self.ValidatePackageDetails()
		return self.res
	
	def FetchFromTrusted(self):
		if self.remote_metadata is None:
			print('Unable to run tests\n')
			return
		url = safe_repo_list[self.repo]+self.remote_metadata['name']
		if self.repo == 3:
			url+= '/json'
		elif self.repo == 2:
			url+= '.json'
		
		self.trusted_metadata = Parser(repo=self.repo).FetchAndParseRemoteTrusted(url)
		
	
	def ValidatePackageDetails(self):
		if self.trusted_metadata is None:
			self.res.update({'WARN':'Unable to find package in public repository, consider reserving this namespace in a public repository'})
		else:
			count = 0
			for key in self.security_features:
				if self.trusted_metadata[key] != self.remote_metadata[key]:
					count +=1
			
			if count <= len(self.security_features)/2 and count > 0:
				self.res.update({'WARN':'Possible dependency confusion attack detected. Review and update packages'})
			elif count > len(self.security_features)/2:
				self.res.update({'ALERT':'Dependency confusion attack detected. Removing package from download list'})
				
				
			

		
		
			
