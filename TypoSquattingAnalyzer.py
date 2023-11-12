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
from multiprocessing import Process,Pool
from threading import Thread

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
			print('INFO: Starting typo squatting analysis...')
			if self.remote_metadata is None or self.remote_metadata['author'] is None or self.remote_metadata['downloads'] is None:
				print(f'ERROR : Package {self.remote_metadata["name"]} missing security features. Unable to analyze for typo squatting attacks')
				return
			self.package_name = self.remote_metadata['name']
			self.GenerateTypos(self.remote_metadata['name'])
			self.FetchPackages()
			self.AnalyzePackagePopularity()
		else:
			print('ERRORL No package information to validate')
		
		print('INFO: Done...')
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
		def insertion_typo_thread(i):
		  	for letter in typos_str:
		  		typo = package_name[:i] + letter + package_name[i:]
		  		if typo not in typos:
		  			typos.append(typo)
	  
		# Generate typos by deletion
		def deletion_typo_thread(i):
			typo = package_name[:i] + package_name[i + 1:]
			if typo not in typos:
		  			typos.append(typo)
	
		# Generate typos by substitution	
		def substitution_typo_thread(i):  
			for letter in typos_str:
				typo = package_name[:i] + letter + package_name[i + 1:]
				if typo not in typos:
		  			typos.append(typo)
	
		# Generate typos by transposition
		def transposition_typo_thread(i):
			typo = package_name[:i] + package_name[i + 1] + package_name[i] + package_name[i + 2:]
			if typo not in typos:
		  			typos.append(typo)
	
		# Generate typos by numeric extension
		def num_ext_typo_thread(i):
			typo = package_name+str(i%10)
			if typo not in typos:
		  			typos.append(typo)
	
		for i in range(len(package_name) + 1):
			insertion_typo_thread(i)
		
		for i in range(len(package_name)):
			deletion_typo_thread(i)
		
		for i in range(len(package_name)):
			substitution_typo_thread(i)
	
		for i in range(len(package_name) - 1):
			transposition_typo_thread(i)
	
		for i in range(len(package_name) - 1):
		 	num_ext_typo_thread(i)
		
		self.candidate_package_names = typos
		
	def FetchRemotePackage(self,url):
		import sys
		sys.stdout.flush()
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
			elif self.repo == 1:
				url+= '.json'
			urls.append(url)	
		
		with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
			executor.map(self.FetchRemotePackage, urls)
		
		
	def AnalyzePackagePopularity(self):
		pkg_download = int(self.remote_metadata['downloads'])
		min_date = datetime.datetime.strptime(self.remote_metadata['age'], '%Y-%m-%dT%H:%M:%S')
		for package in self.packages:
			count = 0
			if int(package['downloads']) > pkg_download and package['downloads'] < 5000:
				count+=1
			if datetime.datetime.strptime(package['age'], '%Y-%m-%dT%H:%M:%S') < min_date:
				count+=1
			if package['author'] and package['author'] not in self.remote_metadata['author']:
				count+=1
			
			if count == 3:
				self.res['ALERT'].append(f'Package {self.remote_metadata["name"]} might be squatted by {package["name"]}. Recheck the package name and public repository.')
				break
