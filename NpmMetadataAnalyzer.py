import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import datetime
import collections
from bs4 import BeautifulSoup

class NpmMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'maintainer', 'keywords', 'project-url', 'license', 'dependencies']
		self.res = {'WARN': [], 'ALERT': [], 'FATAL': []}
		
	def analyze(self):
		self.AnalyzeBaseFeatureSet()
		
		if self.local_metadata is not None:
			print('INFO: Local metadata found, setting local context for analysis...')
			self.AnalyzeVersions()
			self.AnalyzeAuthor()
			self.AnalyzeMaintainers()
			self.AnalyzeProjectURL()
			self.AnalyzeSummary()
			self.AnalyzeLicense()
			self.AnalyzeKeywords()
			self.AnalyzeDependencies()
			self.AnalyzeContextAge()
			self.AnalyzePopularityMetrics()
			self.AnalyzeMissingVersions()
			self.AnalyzeIncreasingVersions()
			self.AnalyzePackageURL()
			

		else:
			
			print('INFO: Local metadata not found, reverting to popularity metrics for analysis...')
			self.AnalyzePopularityMetrics()
			self.AnalyzeMissingVersions()
			self.AnalyzeIncreasingVersions()
			self.AnalyzePackageURL()
		
		
		return self.res
			
	def AnalyzeBaseFeatureSet(self):
		
		if not self.local_metadata is None:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					if not self.local_metadata[key] is None:
						self.res.update['WARN'].append(f'AnalyzeBaseFeatureSet:Mismatch between local and remote {key} packages.')
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res['WARN'].append(f'AnalyzeBaseFeatureSet:A security metadata feature {key} does not have a value.')
	
	def AnalyzeVersions(self):
		if self.local_metadata['version'] and not self.local_metadata['version'] in self.remote_metadata['versions'].keys():
			self.res['ALERT'].append(f'AnalyzeVersions:Version mismatch between local and remote packages') 
			
	def AnalyzeAuthor(self):
		if self.local_metadata['author'] != self.remote_metadata['author']:
			self.res['ALERT'].append(f'AnalyzeAuthor:Author mismatch between local and remote packages')
	
	def AnalyzeMaintainers(self):
		
		remote_maintainer_list = [x["name"] for x in self.remote_metadata['versions'][self.local_metadata['version']]['maintainers']]
		remote_maintainer_email_list = [x["email"] for x in self.remote_metadata['versions'][self.local_metadata['version']]['maintainers']]
		local_maintainer_list = [x for x in self.local_metadata['maintainer']] if self.local_metadata['maintainer'] else None
		local_maintainer_email_list = [x.split(" ")[1].replace("<","").replace(">","") for x in self.local_metadata['maintainer']] if self.local_metadata['maintainer'] else None
		if collections.Counter(remote_maintainer_list) != collections.Counter(local_maintainer_list):
			self.res['ALERT'].append(f'AnalyzeMaintainers:Maintainers mismatch between local and remote packages')
			
		if collections.Counter(remote_maintainer_email_list) != collections.Counter(local_maintainer_email_list):
			self.res['ALERT'].append(f'AnalyzeMaintainers:Maintainers emails mismatch between local and remote packages')
		
	
	def AnalyzeProjectURL(self):
		if self.local_metadata['project-url'] != self.remote_metadata['project-url']:
			self.res['ALERT'].append(f'AnalyzeProjectURL: Project URL mismatch between local and remote packages')
	
	
	def AnalyzeSummary(self):
		if self.local_metadata['summary'] != self.remote_metadata['summary']:
			self.res['ALERT'].append(f'AnalyzeSummary:Summary mismatch between local and remote packages')
			
	def AnalyzeLicense(self):
		if self.local_metadata['license'] != self.remote_metadata['license']:
			self.res['ALERT'].append(f'AnalyzeLicense:License mismatch between local and remote packages')
	
	def AnalyzeKeywords(self):
		
		remote_keywords_list = self.remote_metadata['keywords']
		local_keywords_list = self.local_metadata['keywords']
		
		if collections.Counter(remote_keywords_list) != collections.Counter(local_keywords_list):
			self.res['ALERT'].append(f'AnalyzeKeywords:Keywords mismatch between local and remote packages')
	
	def AnalyzeContextAge(self):
		
		remote_created_date = datetime.datetime.strptime(self.remote_metadata['age']['created'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
		remote_timestamp_for_local = datetime.datetime.strptime(self.remote_metadata['age'][self.local_metadata['version']].split('.')[0], '%Y-%m-%dT%H:%M:%S')

		try:
			package_path = f'/usr/local/lib/node_modules/{self.local_metadata["name"]}'
			creation_timestamp = os.path.getctime(package_path)
			install_date = str(datetime.datetime.fromtimestamp(creation_timestamp).date())+"T"+str(datetime.datetime.fromtimestamp(creation_timestamp).time()).split('.')[0]
			install_date = datetime.datetime.strptime(install_date, '%Y-%m-%dT%H:%M:%S')
			
			if remote_created_date > install_date or install_date < remote_timestamp_for_local:
				self.res['ALERT'].append(f'AnalyzeContextAge:Timestamp mismatch between local and remote packages')
			
		except:
			self.res['WARN'].append(f'AnalyzeContextAge:Unable to fetch Local Metadata timestamps')
		
	def AnalyzeDependencies(self):
		
		remote_dependency_list = list(self.remote_metadata['dependencies'].keys())
		local_dependency_list = list(self.local_metadata['dependencies'].keys())
		remote_dependency_val_list = list(self.remote_metadata['dependencies'].values())
		local_dependency_val_list = list(self.local_metadata['dependencies'].values())
		if collections.Counter(remote_dependency_list) != collections.Counter(local_dependency_list) or collections.Counter(remote_dependency_val_list) != collections.Counter(local_dependency_val_list):
			self.res.update['ALERT'].append(f'AnalyzeDependencies: Dependency mismatch between local and remote packages')
	
	def AnalyzePopularityMetrics(self):
		
		api_url = f'https://api.npmjs.org/downloads/point/last-week/{self.remote_metadata["name"]}'
		res = requests.get(api_url)
		if res.status_code != 200:
			self.res['ALERT'].append(f'AnalyzePopularityMetrics: Unable to fetch package popularity metrics')
			return
		
		if res.json()['downloads'] < 10000:
			self.res['ALERT'].append(f'AnalyzePopularityMetrics: Package is not popular. Recommended test against attack patterns')
			
	
	def AnalyzeMissingVersions(self):
		
		versions = set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys())))
		
		skipped_list = []
		
		for i in range(max(versions)):
			if i not in versions:
				skipped_list.append(i)
				break
		
		if skipped_list:
			self.res['ALERT'].append(f'AnalyzeMissingVersions: Versions {skipped_list} have been skipped')
			
	def AnalyzeIncreasingVersions(self):
		
		versions = list(set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys()))))
		
		for i in range(len(versions)-1):
			if versions[i+1]-versions[i] < 0:
				self.res['ALERT'].append(f'AnalyzeIncreasingVersions: Metadata versions are not strictly increasing: {versions[i+1]}, {versions[i]}')
				break
	
	def AnalyzePackageURL(self):
		
		response = requests.head(self.remote_metadata['project-url'])
		response.raise_for_status()

		# Verify the SSL/TLS certificate
		if not response.ok:
			self.res['ALERT'].append(f'AnalyzePackageURL: Invalid certificate detected for the package')
