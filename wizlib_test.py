"""Unit tests for wizlib.py"""

import unittest
import wizlib


class WordleWizTestBase(unittest.TestCase):
  def setUp(self):
    self.wiz = None
    
  def init(self, words):
    self.wiz = wizlib.WordleWiz(words)
    return self.wiz


class WordleWizCycleTest(WordleWizTestBase):
  """Test the wiz population and scoring methods."""
    
  def test_one_better(self):
    selected = self.init({"aaa", "bbb", "ccc", "abc"}).run_cycle()
    self.assertEqual(selected, "abc")
    for word in self.wiz.possible_words:
      self.assertGreaterEqual(self.wiz.get_score(selected), self.wiz.get_score(word))
    
  def test_all_equal(self):
    selected = self.init({"aaa", "bbb", "ccc"}).run_cycle()
    self.assertEqual(selected, "aaa")
    for word in self.wiz.possible_words:
      self.assertEqual(self.wiz.get_score(selected), self.wiz.get_score(word))
      
  def test_one_worse(self):
    selected = self.init({"abc", "bcb", "cac", "xyz"}).run_cycle()
    self.assertEqual(selected, "abc")
    for word in self.wiz.possible_words:
      self.assertLessEqual(self.wiz.get_score("xyz"), self.wiz.get_score(word))
    
  def test_empty(self):
    with self.assertRaises(wizlib.WordleWizError):
      self.init({})
      
  def test_not_strict(self):
    self.init({"aaa", "bbb", "ccc", "abc"})
    self.wiz._set_possible(("aaa", "bbb", "ccc"))
    selected_strict = self.wiz.run_cycle(strict=True)
    self.assertEqual(selected_strict, "aaa")
    selected_not_strict = self.wiz.run_cycle(strict=False)
    self.assertEqual(selected_not_strict, "abc")
    
  def test_population(self):
    self.init({"aaa", "bbb", "ccc", "abc", "xyz"}).run_cycle()
    self.assertMultiLineEqual(self.wiz.population, """
a: 2, 1, 1, 0, 0, In 2 Words
b: 1, 2, 1, 0, 0, In 2 Words
c: 1, 1, 2, 0, 0, In 2 Words
x: 1, 0, 0, 0, 0, In 1 Words
y: 0, 1, 0, 0, 0, In 1 Words
z: 0, 0, 1, 0, 0, In 1 Words
        """.strip())
    
  def test_score_single_word(self):
    self.init({"aaa"}).run_cycle()
    self.assertEqual(self.wiz.get_score("aaa"), 100)


class WordleWizResultTest(WordleWizTestBase):
  """Test the wiz results and filtering methods."""
  
  def test_simple(self):
    self.init({"aaa", "bbb", "ccc", "abc"}).input_result("abc", "!--")
    self.assertEqual(self.wiz.possible_words, ("aaa", ))
    
  def test_no_words_left(self):
    self.init({"aaa", "bbb", "ccc", "abc"})
    with self.assertRaises(wizlib.WordleWizError):
      self.wiz.input_result("abc", "---")


if __name__ == "__main__":
  unittest.main()