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

separator = '---------------------------------------------------------------------------'

class NpmMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'maintainer', 'keywords', 'project-url', 'license', 'dependencies']
		self.res = {}
	
	def analyze(self):
		print(separator)
		self.AnalyzeBaseFeatureSet()
		
		
		if self.local_metadata is not None:
			print('Reverting to public popularity metrics of the package...')
			print(separator)
			
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
			print('Analyzing package with local metadata data as context...')
			print(separator)
			
			self.AnalyzePopularityMetrics()
			self.AnalyzeMissingVersions()
			self.AnalyzeIncreasingVersions()
			self.AnalyzePackageURL()
			
		return self.res
			
	def AnalyzeBaseFeatureSet(self):
		print('Analyzing base features...')
		print(separator)
		
		if not self.local_metadata is None:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					if not self.local_metadata[key] is None:
						self.res.update({key:{'WARN':f'AnalyzeBaseFeatureSet:Mismatch between local and remote packages.'}})
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res.update({key:{'WARN':f'AnalyzeBaseFeatureSet:A security metadata feature that does not have a value.'}}) 
	
	def AnalyzeVersions(self):
		print('Analyzing versions based on context...')
		print(separator)
		if self.local_metadata['version'] and not self.local_metadata['version'] in self.remote_metadata['versions'].keys():
			self.res.update({'version':{'ALERT':f'AnalyzeVersions:Version mismatch between local and remote packages'}}) 
			
	def AnalyzeAuthor(self):
		print('Analyzing authors based on context...')
		print(separator)
		if self.local_metadata['author'] != self.remote_metadata['author']:
			self.res.update({'author':{'ALERT':f'AnalyzeAuthor:Author mismatch between local and remote packages'}})
	
	def AnalyzeMaintainers(self):
		print('Analyzing maintainers based on context...')
		print(separator)
		
		remote_maintainer_list = [x["name"] for x in self.remote_metadata['versions'][self.local_metadata['version']]['maintainers']]
		remote_maintainer_email_list = [x["email"] for x in self.remote_metadata['versions'][self.local_metadata['version']]['maintainers']]
		local_maintainer_list = [x.split(" ")[0] for x in self.local_metadata['maintainer']] if self.local_metadata['maintainer'] else None
		local_maintainer_email_list = [x.split(" ")[1].replace("<","").replace(">","") for x in self.local_metadata['maintainer']] if self.local_metadata['maintainer'] else None
		if collections.Counter(remote_maintainer_list) != collections.Counter(local_maintainer_list):
			self.res.update({'maintainers':{'ALERT':f'AnalyzeMaintainers:Maintainers mismatch between local and remote packages'}})
			
		if collections.Counter(remote_maintainer_email_list) != collections.Counter(local_maintainer_email_list):
			self.res.update({'maintainers-email':{'ALERT':f'AnalyzeMaintainers:Maintainers emails mismatch between local and remote packages'}})
		
	
	def AnalyzeProjectURL(self):
		print('Analyzing project url based on context...')
		print(separator)
		if self.local_metadata['project-url'] != self.remote_metadata['project-url']:
			self.res.update({'project-url':{'ALERT':f'AnalyzeProjectURL: Project URL mismatch between local and remote packages'}})
	
	
	def AnalyzeSummary(self):
		print('Analyzing summary based on context...')
		print(separator)
		if self.local_metadata['summary'] != self.remote_metadata['summary']:
			self.res.update({'summary':{'ALERT':f'AnalyzeSummary:Summary mismatch between local and remote packages'}})
			
	def AnalyzeLicense(self):
		print('Analyzing license based on context...')
		print(separator)
		if self.local_metadata['license'] != self.remote_metadata['license']:
			self.res.update({'license':{'ALERT':f'AnalyzeLicense:License mismatch between local and remote packages'}})
	
	def AnalyzeKeywords(self):
		print('Analyzing keywords based on context...')
		print(separator)
		
		remote_keywords_list = self.remote_metadata['keywords']
		local_keywords_list = self.local_metadata['keywords']
		
		if collections.Counter(remote_keywords_list) != collections.Counter(local_keywords_list):
			self.res.update({'keywords':{'ALERT':f'AnalyzeKeywords:Keywords mismatch between local and remote packages'}})
	
	def AnalyzeContextAge(self):
		print('Analyzing age based on context...')
		print(separator)
		
		remote_created_date = datetime.datetime.strptime(self.remote_metadata['time']['created'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
		remote_timestamp_for_local = datetime.datetime.strptime(self.remote_metadata['time'][self.local_metadata['version']].split('.')[0], '%Y-%m-%dT%H:%M:%S')

		try:
			package_path = f'/usr/local/lib/node_modules/{self.local_metadata["name"]}'
			creation_timestamp = os.path.getctime(package_path)
			install_date = str(datetime.datetime.fromtimestamp(creation_timestamp).date())+"T"+str(datetime.datetime.fromtimestamp(creation_timestamp).time()).split('.')[0]
			install_date = datetime.datetime.strptime(install_date, '%Y-%m-%dT%H:%M:%S')
			
			if remote_created_date > install_date or install_date < remote_timestamp_for_local:
				self.res.update({'age':{'ALERT':f'AnalyzeContextAge:Timestamp mismatch between local and remote packages'}})
			
		except:
			self.res.update({'age':{'WARN':f'AnalyzeContextAge:Unable to fetch Local Metadata timestamps'}})
		
	def AnalyzeDependencies(self):
		print('Analyzing dependencies based on context...')
		print(separator)
		
		remote_dependency_list = list(self.remote_metadata['dependencies'].keys())
		local_dependency_list = list(self.local_metadata['dependencies'].keys())
		remote_dependency_val_list = list(self.remote_metadata['dependencies'].values())
		local_dependency_val_list = list(self.local_metadata['dependencies'].values())
		if collections.Counter(remote_dependency_list) != collections.Counter(local_dependency_list) or collections.Counter(remote_dependency_val_list) != collections.Counter(local_dependency_val_list):
			self.res.update({'dependencies':{'ALERT':f'AnalyzeDependencies: Dependency mismatch between local and remote packages'}})
	
	def AnalyzePopularityMetrics(self):
		print('Analyzing popularity...')
		
		api_url = f'https://api.npmjs.org/downloads/point/last-week/{self.remote_metadata["name"]}'
		res = requests.get(api_url)
		if res.status_code != 200:
			self.res.update({'popularity':{'ALERT':f'AnalyzePopularityMetrics: Unable to fetch package popularity metrics'}})
			return
		
		if res.json()['downloads'] < 10000:
			self.res.update({'popularity':{'ALERT':f'AnalyzePopularityMetrics: Package is not popular. Recommended test against attack patterns'}})
			
	
	def AnalyzeMissingVersions(self):
		print('Analyzing missing versions...')
		print(separator)
		
		versions = set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys())))
		
		skipped_list = []
		
		for i in range(max(versions)):
			if i not in versions:
				skipped_list.append(i)
				break
		
		if skipped_list:
			self.res.update({'missing-versions':{'ALERT':f'AnalyzeMissingVersions: Versions {skipped_list} have been skipped'}})
			
	def AnalyzeIncreasingVersions(self):
		print('Analyzing strictly increasing versions...')
		print(separator)
		
		versions = list(set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys()))))
		
		for i in range(len(versions)-1):
			if versions[i+1]-versions[i] < 0:
				self.res.update({'increasing-versions':{'ALERT':f'AnalyzeIncreasingVersions: Metadata versions are not strictly increasing: {versions[i+1]}, {versions[i]}'}})
				break
	
	def AnalyzePackageURL(self):
		print('Analyzing certificate validity of URL...')
		print(separator)
		
		response = requests.head(self.remote_metadata['project-url'])
		response.raise_for_status()

		# Verify the SSL/TLS certificate
		if not response.ok:
			self.res.update({'project-url':{'ALERT':f'AnalyzePackageURL: Invalid certificate detected for the package'}})
