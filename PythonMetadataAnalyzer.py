import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import datetime
from bs4 import BeautifulSoup

separator = '---------------------------------------------------------------------------'

class PythonMetadataAnalyzer:
	def __init__(self, remote_metadata, local_metadata):
		self.remote_metadata, self.local_metadata = remote_metadata, local_metadata
		self.keys = ['name', 'version', 'summary', 'author', 'author-email', 'maintainer', 'maintainer-email', 'project-url', 'license', 'dependencies']
		self.res = {}
	
	def analyze(self):
		print(separator)
		self.AnalyzeBaseFeatureSet()
			
		if self.local_metadata is not None:
			print('Analyzing package with local metadata data as context...')
			print(separator)
			
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
			print('Reverting to public popularity metrics of the package...')
			print(separator)
			
			self.AnalyzePopularityMetrics()
			self.AnalyzeMissingVersions()
			self.AnalyzeIncreasingVersions()
			self.AnalyzePackageURL()
			
		return self.res
			
	def AnalyzeBaseFeatureSet(self):
		print('Analyzing base features...')
		print(separator)
		rem_keys = [self.remote_metadata.keys() - self.keys]
		
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
		
		if not self.local_metadata['version'] or not self.remote_metadata['versions']:
			self.res.update({'FATAL':'AnalyzeVersionsTest:Versions metadata value missing'})
			return
		
		if self.local_metadata['version'] and not self.local_metadata['version'] in self.remote_metadata['versions'].keys():
			self.res.update({'version':{'ALERT':f'AnalyzeVersions:Version mismatch between local and remote packages'}}) 
			
	def AnalyzeAuthor(self):
		print('Analyzing authors based on context...')
		print(separator)
		
		if not self.remote_metadata['author'] or not self.remote_metadata['author-email']:
			self.res.update({'FATAL':'AnalyzeAuthorTest:Authors metadata value missing'})
			return
		
		if self.local_metadata['author'] != self.remote_metadata['author'] and not self.local_metadata['author'] in self.remote_metadata['author-email']:
			self.res.update({'author':{'ALERT':f'AnalyzeAuthor:Author mismatch between local and remote packages'}}) 
		
		if self.local_metadata['author-email'] != self.remote_metadata['author-email'] and self.local_metadata['author-email'] not in self.remote_metadata['author-email']:
			self.res.update({'author-email':{'ALERT':f'AnalyzeAuthor:Author email mismatch between local and remote packages'}}) 
	
	def AnalyzeMaintainers(self):
		print('Analyzing maintainers based on context...')
		print(separator)
		
		if not self.remote_metadata['maintainer'] or not self.remote_metadata['maintainer-email']:
			self.res.update({'FATAL':'AnalyzeMaintainerTest:Maintainers metadata value missing'})
			return
		
		if self.local_metadata['maintainer'] != self.remote_metadata['maintainer'] and self.local_metadata['maintainer'] not in self.remote_metadata['maintainer-email']:
			self.res.update({'maintainer':{'ALERT':f'AnalyzeMaintainers:Maintainer mismatch between local and remote packages'}})
			
		if self.local_metadata['maintainer-email'] != self.remote_metadata['maintainer-email']:
			self.res.update({'maintainer-email':{'ALERT':f'AnalyzeMaintainers:Maintainer Email mismatch between local and remote packages'}}) 
	
	def AnalyzeProjectURL(self):
		print('Analyzing project url based on context...')
		print(separator)
		if self.local_metadata['project-url'] != self.remote_metadata['project-url']:
			self.res.update({'maintainer':{'ALERT':f'AnalyzeProjectURL: Project URL mismatch between local and remote packages'}})
	
	
	def AnalyzeSummary(self):
		print('Analyzing summary based on context...')
		print(separator)
		if self.local_metadata['summary'] != self.remote_metadata['summary']:
			self.res.update({'summary':{'ALERT':f'AnalyzeSummary:Summary mismatch between local and remote packages'}})
			
	def AnalyzeLicense(self):
		print('Analyzing license based on context...')
		print(separator)
		
		if not self.local_metadata['license'] or not self.remote_metadata['license']:
			self.res.update({'FATAL':'AnalyzeLicenseTest:License metadata value missing'})
			return
		
		if self.local_metadata['license'] != self.remote_metadata['license'] and self.local_metadata['license'][:3] not in self.remote_metadata['license']:
			self.res.update({'license':{'ALERT':f'AnalyzeLicense:License mismatch between local and remote packages'}})
	
	def AnalyzeContextAge(self):
		print('Analyzing age based on context...')
		print(separator)
		try:
			distribution = pkg_resources.get_distribution(self.local_metadata['name'])
			distribution_location = distribution.location
			package_path = os.path.join(distribution_location, self.local_metadata['name'])
			creation_timestamp = os.path.getctime(package_path)
			install_date = str(datetime.datetime.fromtimestamp(creation_timestamp).date())+"T"+str(datetime.datetime.fromtimestamp(creation_timestamp).time()).split('.')[0]
			
			if self.local_metadata['version'] in self.res.keys():
				self.res.update({'age':{'ALERT':f'AnalyzeContextAge:Unable to validate timestamp due to version mismatch'}})
				
			release_date = self.remote_metadata['versions'][self.local_metadata['version']][0]['upload_time']
			
			
			install_date = datetime.datetime.strptime(install_date, '%Y-%m-%dT%H:%M:%S')
			release_date = datetime.datetime.strptime(release_date, '%Y-%m-%dT%H:%M:%S')
			
			
			if release_date > install_date:
				self.res.update({'age':{'ALERT':f'AnalyzeContextAge:Remote package has a timestamp greater than '}})
		except:
			self.res.update({'age':{'WARN':f'AnalyzeContextAge:Unable to fetch Local Metadata timestamps'}})
			
	def AnalyzeDependencies(self):
		print('Analyzing license based on context...')
		print(separator)
		
		if not self.remote_metadata['dependencies'] or not self.remote_metadata['dependencies']:
			self.res.update({'FATAL':'AnalyzeDependenciesTest:Dependency metadata value missing'})
			return
		
		if self.local_metadata['dependencies'] != self.remote_metadata['dependencies'] and self.local_metadata['dependencies'] not in self.remote_metadata['dependencies']:
			self.res.update({'license':{'ALERT':f'AnalyzeDependencies: Dependency mismatch between local and remote packages'}})
	
	def AnalyzePopularityMetrics(self):
		print('Analyzing popularity...')
		print(separator)
		api_url = f'https://pypistats.org/api/packages/{self.remote_metadata["name"]}/recent'
		response = requests.get(api_url)
		if response.status_code == 200:
			downloads = response.json()['data']
			week_download_stats = downloads['last_week']
			month_download_stats = downloads['last_month']
			day_download_stats = downloads['last_day']
			
			# check the three values
			if day_download_stats == week_download_stats and week_download_stats == month_download_stats:
				self.res.update({'popularity':{'WARN':f'AnalyzePopularityMetrics: Package is new, recommended validation against attack patterns'}})
			
			if int(week_download_stats) < 10000:
				self.res.update({'popularity':{'ALERT':f'AnalyzePopularityMetrics: Package below threshold for downloads, recommended validation against attack patterns'}})
		else:
			return None		
	
	def AnalyzeMissingVersions(self):
		print('Analyzing missing versions...')
		print(separator)
		
		versions = list(map(lambda x : int(x.split('.')[0]),list(self.remote_metadata['versions'].keys())))
		skipped_list = []
		for i in range(max(versions)):
			if i not in versions:
				skipped_list.append(i)
		
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
		
		if self.remote_metadata['project-url'] is None:
			self.res.update({'project-url':{'ALERT':f'AnalyzePackageURL: Package does not have a valid URL'}})
			return
		
		try:
			response = requests.head(self.remote_metadata['project-url'])
			response.raise_for_status()

			# Verify the SSL/TLS certificate
			if not response.ok:
				self.res.update({'project-url':{'ALERT':f'AnalyzePackageURL: Invalid certificate detected for the package'}})
		except:
				self.res.update({'project-url':{'ALERT':f'AnalyzePackageURL: Failed to fetch certiciate for the package'}})
