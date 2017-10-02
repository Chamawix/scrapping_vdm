import unittest

import form
import extractor
from app import launch
from app import is_between_time




#Methodes de tests automatises de notre application
class TestMethods(unittest.TestCase):
	def setUp(self):
		self.ex = extractor.Extractor()
		self.s_date = "zeizo"
		self.e_date="0"
		self.check_date ="3829"
		self.ask = form.Form()

	def test_form(self):
		self.assertTrue(self.ask.request_form()== -1 or type(self.ask.request_form()) is str)

	def test_extraction_liste_liens(self):
		self.assertFalse(self.ex.extractArticleListToExplore(1) == -1)

	def test_explore_article(self):
		self.assertFalse(self.ex.exploreArticle("") == -1)

	def test_in_between_date(self):
		self.assertTrue(type(is_between_time(self.s_date, self.e_date, self.check_date)) is bool)

	def test_format_date(self):
 		self.assertTrue(type((extractor.format_date(self.check_date))) is str)

if __name__ == "__main__":
	unittest.main()