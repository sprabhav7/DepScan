import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import datetime
import logging

from DependencyConfusionAnalyzer import DependencyConfusionAnalyzer
from bs4 import BeautifulSoup


class PythonMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'author-email', 'maintainer', 'maintainer-email', 'project-url', 'license', 'dependencies']
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
		
		rem_keys = [self.remote_metadata.keys() - self.keys]
		
		if not self.local_metadata is None:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					if not self.local_metadata[key] is None:
						self.res['WARN'].append(f'AnalyzeBaseFeatureSet:Mismatch between local and remote {key} packages.')
		else:
			for key in self.keys:
				if self.remote_metadata[key] is None:
					self.res['WARN'].append(f'AnalyzeBaseFeatureSet:A security metadata feature {key} does not have a value.') 
	
	def AnalyzeVersions(self):
		
		if not self.local_metadata['version'] or not self.remote_metadata['versions']:
			self.res['ALERT'].append('AnalyzeVersionsTest:Versions metadata value missing')
			return
		
		if self.local_metadata['version'] and not self.local_metadata['version'] in self.remote_metadata['versions'].keys():
			self.res['ALERT'].append(f'AnalyzeVersionsTest:Version mismatch between local and remote packages')
 
			
	def AnalyzeAuthor(self):
		
		if not self.remote_metadata['author'] or not self.remote_metadata['author-email']:
			self.res['WARN'].append('AnalyzeAuthorTest:Authors metadata value missing')
			return
		
		if self.local_metadata['author'] != self.remote_metadata['author'] and not self.local_metadata['author'] in self.remote_metadata['author-email']:
			self.res['ALERT'].append(f'AnalyzeAuthorTest:Author mismatch between local and remote packages')
 
		
		if self.local_metadata['author-email'] != self.remote_metadata['author-email'] and self.local_metadata['author-email'] not in self.remote_metadata['author-email']:
			self.res['ALERT'].append(f'AnalyzeAuthorTest:Author email mismatch between local and remote packages')
 
	
	def AnalyzeMaintainers(self):
		
		if not self.remote_metadata['maintainer'] or not self.remote_metadata['maintainer-email']:
			self.res['WARN'].append('AnalyzeMaintainerTest:Maintainers metadata value missing')
			return
		
		if self.local_metadata['maintainer'] != self.remote_metadata['maintainer'] and self.local_metadata['maintainer'] not in self.remote_metadata['maintainer-email']:
			self.res['ALERT'].append(f'AnalyzeMaintainersTest: Maintainer mismatch between local and remote packages')
			
		if self.local_metadata['maintainer-email'] != self.remote_metadata['maintainer-email']:
			self.res['ALERT'].append(f'AnalyzeMaintainersTest: Maintainer Email mismatch between local and remote packages')
 
	
	def AnalyzeProjectURL(self):
		
		if self.local_metadata['project-url'] != self.remote_metadata['project-url']:
			self.res['ALERT'].append(f'AnalyzeProjectURLTest: Project URL mismatch between local and remote packages')
	
	
	def AnalyzeSummary(self):
		
		if self.local_metadata['summary'] != self.remote_metadata['summary']:
			self.res['ALERT'].append(f'AnalyzeSummaryTest: Summary mismatch between local and remote packages')
			
	def AnalyzeLicense(self):
		
		if not self.local_metadata['license'] or not self.remote_metadata['license']:
			self.res['ALERT'].append('AnalyzeLicenseTest: License metadata value missing')
			return
		
		if self.local_metadata['license'] != self.remote_metadata['license'] and self.local_metadata['license'][:3] not in self.remote_metadata['license']:
			self.res['ALERT'].append(f'AnalyzeLicenseTest: License mismatch between local and remote packages')
	
	def AnalyzeContextAge(self):
		
		try:
			distribution = pkg_resources.get_distribution(self.local_metadata['name'])
			distribution_location = distribution.location
			package_path = os.path.join(distribution_location, self.local_metadata['name'])
			creation_timestamp = os.path.getctime(package_path)
			install_date = str(datetime.datetime.fromtimestamp(creation_timestamp).date())+"T"+str(datetime.datetime.fromtimestamp(creation_timestamp).time()).split('.')[0]
			
			if self.local_metadata['version'] in self.res.keys():
				self.res['ALERT'].append(f'AnalyzeContextAge:Unable to validate timestamp due to version mismatch')
				
			release_date = self.remote_metadata['versions'][self.local_metadata['version']][0]['upload_time']
			
			
			install_date = datetime.datetime.strptime(install_date, '%Y-%m-%dT%H:%M:%S')
			release_date = datetime.datetime.strptime(release_date, '%Y-%m-%dT%H:%M:%S')
			
			if release_date > install_date:
				self.res['ALERT'].append(f'AnalyzeContextAgeTest: Remote package has a timestamp greater than ')
		except:
			self.res['FATAL'].append(f'AnalyzeContextAgeTest: Unable to fetch Local Metadata timestamps')
			
	def AnalyzeDependencies(self):
		
		if not self.local_metadata['dependencies'] or not self.remote_metadata['dependencies']:
			return
		
		if self.local_metadata['dependencies'] != self.remote_metadata['dependencies'] and self.local_metadata['dependencies'] not in self.remote_metadata['dependencies']:
			self.res['ALERT'].append(f'AnalyzeDependenciesTest: Dependency mismatch between local and remote packages')
	
	def AnalyzePopularityMetrics(self):
		
		api_url = f'https://pypistats.org/api/packages/{self.remote_metadata["name"]}/recent'
		response = requests.get(api_url)
		if response.status_code == 200:
			downloads = response.json()['data']
			week_download_stats = downloads['last_week']
			month_download_stats = downloads['last_month']
			day_download_stats = downloads['last_day']
			
			# check the three values
			if day_download_stats == week_download_stats and week_download_stats == month_download_stats:
				self.res['WARN'].append(f'AnalyzePopularityMetricsTest: Package is new, recommended validation against attack patterns')
			
			if int(week_download_stats) < 10000:
				self.res['ALERT'].append(f'AnalyzePopularityMetricsTest: Package below threshold for downloads, recommended validation against attack patterns')
		else:
			return None		
	
	def AnalyzeMissingVersions(self):
		
		versions = list(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys())))
		skipped_list = []
		for i in range(max(versions)):
			if i not in versions and i > 0:
				skipped_list.append(i)
		
		if skipped_list:
			self.res['ALERT'].append(f'AnalyzeMissingVersionsTest: Versions {skipped_list} have been skipped')
			
	def AnalyzeIncreasingVersions(self):
		
		versions = list(set(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys()))))
		
		for i in range(len(versions)-1):
			if versions[i+1]-versions[i] < 0:
				self.res['ALERT'].append(f'AnalyzeIncreasingVersionsTest: Metadata versions are not strictly increasing: {versions[i+1]}, {versions[i]}')
				break
	
	def AnalyzePackageURL(self):
		
		if self.remote_metadata['project-url'] is None:
			self.res['ALERT'].append(f'AnalyzePackageURLTest: Package does not have a valid URL')
			return
		
		try:
			response = requests.head(self.remote_metadata['project-url'])
			response.raise_for_status()

			# Verify the SSL/TLS certificate
			if not response.ok:
				self.res['ALERT'].append(f'AnalyzePackageURLTest: Invalid certificate detected for the package')
		except:
				self.res['FATAL'].append(f'AnalyzePackageURLTest: Failed to fetch certiciate for the package')
