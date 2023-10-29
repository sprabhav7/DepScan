import importlib
import importlib.metadata
import requests
import pkg_resources
from bs4 import BeautifulSoup


class PythonMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		print('Initialized Python Analyzer...')
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'author-email', 'maintainer', 'maintainer-email', 'project-url', 'license', 'dependencies']
		self.res = {}
	
	def analyze(self):
		self.AnalyzeBaseFeatureSet()
		self.AnalyzeVersions()
		self.AnalyzeAuthor()
		self.AnalyzeMaintainers()
		'''self.AnalyzeTypoSquatting()
		self.AnalyzeDependencyConfusionAttack()
		
		if local_metadata is None:
			self.AnalyzePopularityMetrics()
			self.AnalyzePackageAge()
			self.ValidateProjectURL()
			self.AnalyzeImmaturePackage()
			self.AnalyzeFirstPackage()
			self.MissingVersions()
			

		else:
			self.AnalyzeVersions()
			self.ValidateDependencies()
			self.AnalyzeAuthors()
			self.AnalyzeMaintainers()
			self.ValidateChecksum()
			self.AnalyzeProjectURL()'''
		return self.res
			
	def AnalyzeBaseFeatureSet(self):
		rem_keys = [self.remote_metadata.keys() - self.keys]
		
		if not self.local_metadata is None:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					if not self.local_metadata[key] is None:
						self.res.update({key:{'ALERT':f'Values are different between local and remote packages.'}})
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res.update({key:{'WARN':f'A security metadata feature that does not have a value.'}}) 
	
	def AnalyzeVersions(self):
		if self.local_metadata['version'] and not self.local_metadata['version'] in self.remote_metadata['versions'].keys():
			self.res.update({'version':{'ALERT':f'Remote package does not have {self.local_metadata["version"]} in the list of versions.'}}) 
			
	def AnalyzeAuthor(self):
		if self.local_metadata['author'] != self.remote_metadata['author']:
			self.res.update({'author':{'ALERT':f'Remote package {self.remote_metadata["author"]} does not match local package {self.local_metadata["author"]}.'}}) 
		
		if self.local_metadata['author-email'] != self.remote_metadata['author-email']:
			self.res.update({'author-email':{'ALERT':f'Remote package {self.remote_metadata["author-email"]} does not match local package {self.local_metadata["author-email"]}.'}}) 
	
	def AnalyzeMaintainers(self):
		if self.local_metadata['maintainer'] != self.remote_metadata['maintainer']:
			self.res.update({'maintainer':{'ALERT':f'Remote package {self.remote_metadata["maintainer"]} does not match local package {self.local_metadata["maintainer"]}.'}})
			
		if self.local_metadata['maintainer-email'] != self.remote_metadata['maintainer-email']:
			self.res.update({'maintainer-email':{'ALERT':f'Remote package {self.remote_metadata["maintainer-email"]} does not match local package {self.local_metadata["maintainer-email"]}.'}}) 
	
	
	def AnalyzeTypoSquatting(self, package_name):
		return 'Hello World'
	
	def DependencyConfusionAttack(self,package_name):
		return 'Hello World'
