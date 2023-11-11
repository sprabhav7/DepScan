from TypoSquattingAnalyzer import TypoSquattingAnalyzer
from DependencyConfusionAnalyzer import DependencyConfusionAnalyzer


class AttackAnalyzer:
	def __init__(self, remote_metadata, repo, options):
		self.remote_metadata = remote_metadata
		self.repo = repo
		self.option = options
		self.res = {}
	
	def Analyzer(self):
		if self.option == '-d':
			self.res['Confusion-Analysis'] = DependencyConfusionAnalyzer(self.remote_metadata,self.repo).analyze()
		elif self.option == '-t':
			self.res['Typosquatting-Analysis'] = TypoSquattingAnalyzer(self.remote_metadata,self.repo).analyze()
		else:
			self.res['Confusion-Analysis'] = DependencyConfusionAnalyzer(self.remote_metadata,self.repo).analyze()
			self.res['Typosquatting-Analysis'] = TypoSquattingAnalyzer(self.remote_metadata,self.repo).analyze()
		
		return self.res
		
