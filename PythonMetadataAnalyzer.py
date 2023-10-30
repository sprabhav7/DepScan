import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
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
			self.ValidateLocalChecksum()
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
			self.res.update({'author':{'ALERT':f'Remote package : {self.remote_metadata["author"]} ; Local package : {self.local_metadata["author"]}.'}}) 
		
		if self.local_metadata['author-email'] != self.remote_metadata['author-email']:
			self.res.update({'author-email':{'ALERT':f'Remote package : {self.remote_metadata["author-email"]} ; Local package : {self.local_metadata["author-email"]}.'}}) 
	
	def AnalyzeMaintainers(self):
		if self.local_metadata['maintainer'] != self.remote_metadata['maintainer']:
			self.res.update({'maintainer':{'ALERT':f'Remote package : {self.remote_metadata["maintainer"]} ; Local package : {self.local_metadata["maintainer"]}.'}})
			
		if self.local_metadata['maintainer-email'] != self.remote_metadata['maintainer-email']:
			self.res.update({'maintainer-email':{'ALERT':f'Remote package : {self.remote_metadata["maintainer-email"]} ; Local package : {self.local_metadata["maintainer-email"]}.'}}) 
	'''
	def ValidateLocalChecksum(self):
		pkg_sha256 = self.remote_metadata['versions'][self.local_metadata['version']][0]['digests']['sha256']
		print(pkg_sha256)
		exit(1)
		if 'version' in self.res.keys():
			 #do some errors stuff
			 return
			 
		package_data = pkgutil.get_data(self.local_metadata['name'], "__init__.py")
		if package_data is None:
			raise FileNotFoundError("Package not found or has no '__init__.py' file")
		
		hash_algorithm = hashlib.sha256()  # You can choose a different hashing algorithm
		hash_algorithm.update(package_data)
		calculated_hash = hash_algorithm.hexdigest()
		print(calculated_hash)
	'''	
	
	def AnalyzeTypoSquatting(self, package_name):
		return 'Hello World'
	
	def AnalyzeDependencyConfusion(self,package_name):
		return 'Hello World'
