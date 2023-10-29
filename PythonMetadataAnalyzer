import importlib
import importlib.metadata
import requests
import pkg_resources
from bs4 import BeautifulSoup


class PythonMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		print('Initialized Python Analyzer...')
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'maintainer', 'project-url', 'license', 'dependencies']
		self.res = {}
	
	def analyze(self):
		self.AnalyzeBaseFeatureSet()
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
						self.res[key].append({'ALERT':f'{key} values are different between local and remote packages.'})
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res[key].append({'WARN':f'{key} is a security metadata feature that does not have a value.'}) 
	
	
	def AnalyzeTypoSquatting(self, package_name):
		return 'Hello World'
	
	def DependencyConfusionAttack(self,package_name):
		return 'Hello World'
