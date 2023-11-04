import importlib
import importlib.metadata
import requests
import hashlib
import pkg_resources
import pkgutil
import os
import datetime
import random
from bs4 import BeautifulSoup
from ParseUtil import Parser
import concurrent.futures
import subprocess
from multiprocessing import Process

safe_repo_list = {
1: 'https://rubygems.org/api/v1/gems/',
2: 'https://registry.npmjs.org/',
3: 'https://pypi.org/pypi/'
}

class TypoSquattingAnalyzer:
	def __init__(self, remote_metadata,repo):
		self.remote_metadata= remote_metadata
		self.repo = repo
		self.parser = None
		self.package_name = None
		self.res = {'WARN': [], 'ALERT': [], 'FATAL': []}
		self.packages = []
		self.candidate_package_names = []
		self.nbrs = {}
		self.nbrs['q'] = "qwas"
		self.nbrs['w'] = "wqasde"
		self.nbrs['e'] = "wsdfrae"
		self.nbrs['r'] = "edfgtr"
		self.nbrs['t'] = "rfghyt"
		self.nbrs['y'] = "tghjuy"
		self.nbrs['u'] = "yhjkiu"
		self.nbrs['i'] = "ujkloi"
		self.nbrs['o'] = "iklpo"
		self.nbrs['p'] = "plo['ik"
		self.nbrs['a'] = "qazxsdwce"
		self.nbrs['s'] = "qazxcdews"
		self.nbrs['d'] = "wsxcvfred"
		self.nbrs['f'] = "edcvbgtrf"
		self.nbrs['g'] = "rfvbnhytg"
		self.nbrs['h'] = "tgbnmjuyh"
		self.nbrs['j'] = "yhnm,kiuj"
		self.nbrs['k'] = "ujm,k.loi"
		self.nbrs['l'] = "ik,.;pol"
		self.nbrs['z'] = "asxz"
		self.nbrs['x'] = "zasdcx"
		self.nbrs['c'] = "xsdfvc"
		self.nbrs['v'] = "cdfgbv"
		self.nbrs['b'] = "vfghnb"
		self.nbrs['n'] = "bghjmn"
		self.nbrs['m'] = "nhjk,m"
		self.nbrs[' '] = " "
	
	def analyze(self):
		if self.remote_metadata:
			self.package_name = self.remote_metadata['name']
			self.GenerateTypos(self.remote_metadata['name'])
			self.FetchPackages()
			self.AnalyzePackagePopularity()
		else:
			print('No package information to validate')
		
		return self.res
		
	
	def GenerateValidTypoPool(self):
		typos=''
		for char in self.package_name:
			if char in self.nbrs:
				typos += self.nbrs[char]
		
		return ''.join(e for e in set(typos))
	
	def GenerateTypos(self,package_name):
		typos = []
		typos_str = self.GenerateValidTypoPool()
		# Generate typos by insertion
		for i in range(len(package_name) + 1):
		  	for letter in typos_str:
		  		typo = package_name[:i] + letter + package_name[i:]
		  		if typo not in typos:
		  			typos.append(typo)
		  
		# Generate typos by deletion
		for i in range(len(package_name)):
			typo = package_name[:i] + package_name[i + 1:]
			if typo not in typos:
		  			typos.append(typo)
		  
		# Generate typos by substitution
		for i in range(len(package_name)):
			for letter in typos_str:
				typo = package_name[:i] + letter + package_name[i + 1:]
				if typo not in typos:
		  			typos.append(typo)
		  
		# Generate typos by transposition
		for i in range(len(package_name) - 1):
			typo = package_name[:i] + package_name[i + 1] + package_name[i] + package_name[i + 2:]
			if typo not in typos:
		  			typos.append(typo)
			
		# Generate typos by numeric extension
		for i in range(len(package_name) - 1):
			typo = package_name+str(i%10)
			if typo not in typos:
		  			typos.append(typo)
		
		self.candidate_package_names = typos
		
	def FetchRemotePackage(self,url):
		metadata = self.parser.FetchAndParseRemoteTrusted(url)
		if metadata is not None:
			self.packages.append(metadata)
			
	def FetchPackages(self):
		self.parser = Parser(repo=self.repo)
		urls = []

		for package in self.candidate_package_names:
			url = safe_repo_list[self.repo]+package
			if self.repo == 3:
				url+= '/json'
			elif self.repo == 2:
				url+= '.json'
			urls.append(url)
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.map(self.FetchRemotePackage, urls)
		
		
	def AnalyzePackagePopularity(self):
		pkg_download = int(self.remote_metadata['downloads'])
		min_date = datetime.datetime.strptime(self.remote_metadata['age'], '%Y-%m-%dT%H:%M:%S')
		for package in self.packages:
			if int(package['downloads']) > pkg_download:
				self.res['ALERT'].append('Package {remote_metadata["name"]} has squatted packages with similar popularity. Check for squatting attacks')
				break
			if datetime.datetime.strptime(package['age'], '%Y-%m-%dT%H:%M:%S') < min_date:
				self.res['ALERT'].append('Package {remote_metadata["name"]} is now the oldest package in the squatting range. Check for squatting attacks')
				break
			if package['author'] and package['author'] not in self.remote_metadata['author']:
				self.res['ALERT'].append('Package {remote_metadata["name"]} might be squatted. Check for squatting attacks')
				break
			
