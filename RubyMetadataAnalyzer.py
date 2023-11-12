import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import datetime
import collections
import subprocess
from bs4 import BeautifulSoup


class RubyMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'metadata', 'project-url', 'license', 'dependencies']
		self.res = {'WARN': [], 'ALERT': [], 'FATAL': []}
	
	def analyze(self):
		self.AnalyzeBaseFeatureSet()
		
		
		if self.local_metadata is not None:
		
			print('INFO: Local metadata found, setting local context for analysis...')
			self.AnalyzeVersions() #maybe remove
			self.AnalyzeAuthor()
			self.AnalyzeProjectURL()
			self.AnalyzeSummary()
			self.AnalyzeLicense()
			self.AnalyzeContextAge()
			self.AnalyzeDependencies()
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
		if self.local_metadata['version'] and self.local_metadata['version']['version']  not in self.remote_metadata['versions']:
			self.res['ALERT'].append(f'AnalyzeVersions:Version mismatch between local and remote packages') 
			
	def AnalyzeAuthor(self):
		
		for author in self.local_metadata['author']:
			if author not in self.remote_metadata['author']:
				self.res['ALERT'].append(f'AnalyzeAuthor:Author mismatch between local and remote packages')
	
	def AnalyzeProjectURL(self):
		
		if self.local_metadata['project-url'] != self.remote_metadata['project-url']:
			self.res['ALERT'].append(f'AnalyzeProjectURL: Project URL mismatch between local and remote packages')
	
	
	def AnalyzeSummary(self):
		
		if self.local_metadata['summary'] != self.remote_metadata['summary']:
			self.res['ALERT'].append(f'AnalyzeSummary:Summary mismatch between local and remote packages')
			
	def AnalyzeLicense(self):
		
		if collections.Counter(self.local_metadata['license']) != collections.Counter(self.remote_metadata['license']):
			self.res['ALERT'].append(f'AnalyzeLicense:License mismatch between local and remote packages')
	
	def AnalyzeContextAge(self):
		
		if datetime.datetime.strptime(self.remote_metadata['age'].split('T')[0], '%Y-%m-%d') < datetime.datetime.strptime(self.local_metadata['age'].split('T')[0], '%Y-%m-%d'):
			self.res['WARN'].append(f'AnalyzeContextAge:Invalid metadata timestamps')
		
		
	def AnalyzeDependencies(self):
		
		remote_dependency_list = list(x['name'] for x in self.remote_metadata['dependencies']['runtime'])
		local_dependency_list = list(x['name'] for x in self.local_metadata['dependencies'])
		if collections.Counter(remote_dependency_list) != collections.Counter(local_dependency_list):
			self.res['ALERT'].append(f'AnalyzeDependencies: Dependency mismatch between local and remote packages')
	
	def AnalyzePopularityMetrics(self):
		
		if self.remote_metadata['downloads']<10000:
			self.res['ALERT'].append(f'AnalyzePopularityMetrics: Package is not popular. Recommended test against attack patterns')
			
	
	def AnalyzeMissingVersions(self):
		
		versions = set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'])))
		
		skipped_list = []
		
		for i in range(max(versions)):
			if i not in versions:
				skipped_list.append(i)
				break
		
		if skipped_list:
			self.res['ALERT'].append(f'AnalyzeMissingVersions: Versions {skipped_list} have been skipped')
			
	def AnalyzeIncreasingVersions(self):
		
		versions = list(set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions']))))
		
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
