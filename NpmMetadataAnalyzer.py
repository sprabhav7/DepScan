import importlib
import importlib.metadata
import requests
import pkg_resources
from bs4 import BeautifulSoup


class NpmMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		print('Initialized NPM Analyzer...')
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'maintainer', 'project-url', 'license', 'dependencies']
		self.res={}
	
	def AnalyzeBaseFeatureSet(self):
		if not self.local_metadata is None:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					if not self.local_metadata[key] is None:
						self.res.update({key:{'ALERT':f'{key} values are different between local - {self.local_metadata[key]} and remote packages -{self.remote_metadata[key]}.'}})
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res.update({key:{'WARN':f'{key} is a security metadata feature that does not have a value.'}}) 
					
	def analyze(self):
		self.AnalyzeBaseFeatureSet()
		return self.res
