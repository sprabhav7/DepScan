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

separator = '---------------------------------------------------------------------------'

class RubyMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'metadata', 'project-url', 'license', 'dependencies']
		self.res = {}
	
	def analyze(self):
		print(separator)
		self.AnalyzeBaseFeatureSet()
		
		
		if self.local_metadata is not None:
			print('Reverting to public popularity metrics of the package...')
			print(separator)
		
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
		if self.local_metadata['version'] and self.local_metadata['version']['version']  not in self.remote_metadata['versions']:
			self.res.update({'version':{'ALERT':f'AnalyzeVersions:Version mismatch between local and remote packages'}}) 
			
	def AnalyzeAuthor(self):
		print('Analyzing authors based on context...')
		print(separator)
		for author in self.local_metadata['author']:
			if author not in self.remote_metadata['author']:
				self.res.update({'author':{'ALERT':f'AnalyzeAuthor:Author mismatch between local and remote packages'}})
	
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
		if collections.Counter(self.local_metadata['license']) != collections.Counter(self.remote_metadata['license']):
			self.res.update({'license':{'ALERT':f'AnalyzeLicense:License mismatch between local and remote packages'}})
	
	def AnalyzeContextAge(self):
		print('Analyzing age based on context...')
		print(separator)
		
		if datetime.datetime.strptime(self.remote_metadata['time'], '%Y-%m-%d') < datetime.datetime.strptime(self.local_metadata['time'], '%Y-%m-%d'):
			self.res.update({'age':{'WARN':f'AnalyzeContextAge:Invalid metadata timestamps'}})
		
		
	def AnalyzeDependencies(self):
		print('Analyzing dependencies based on context...')
		print(separator)
		
		remote_dependency_list = list(x['name'] for x in self.remote_metadata['dependencies']['runtime'])
		local_dependency_list = list(x['name'] for x in self.local_metadata['dependencies'])
		if collections.Counter(remote_dependency_list) != collections.Counter(local_dependency_list):
			self.res.update({'dependencies':{'ALERT':f'AnalyzeDependencies: Dependency mismatch between local and remote packages'}})
	
	def AnalyzePopularityMetrics(self):
		print('Analyzing popularity...')
		print(separator)
		
		if self.remote_metadata['downloads']<10000:
			self.res.update({'popularity':{'ALERT':f'AnalyzePopularityMetrics: Package is not popular. Recommended test against attack patterns'}})
			
	
	def AnalyzeMissingVersions(self):
		print('Analyzing missing versions...')
		print(separator)
		
		versions = set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'])))
		
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
		
		versions = list(set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions']))))
		
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
