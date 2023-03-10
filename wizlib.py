"""Play the Wordle game.

Look at the population of letters in all possible words, and then score each word for its benefit.
Select the word with the higher score in each cycle.
For the scoring algorithm see _score.
"""
import collections
import dataclasses
import functools
import operator
import string

from typing import Dict, List, Set, Optional
from ww_utils import ResultChars, POSSIBLE_RESULT_CHARS, MAX_WORD_LEN, LETTERS


class WordleWizError(Exception):
  pass


@dataclasses.dataclass
class Population:
  """The population of a single letter in all possible words."""
  word_count: int = 0 
  position_count: List[int] = dataclasses.field(default_factory=lambda: [0] * MAX_WORD_LEN)
  
  def __repr__(self):
    return (
        ", ".join(str(p) for p in self.position_count)
        + (", In %s Words" % self.word_count))
  

@dataclasses.dataclass
class Knowladge:
  """What we know about a single letter."""
  not_in_word: bool = False
  in_position: Set[int] = dataclasses.field(default_factory=set)
  not_in_position: Set[int] = dataclasses.field(default_factory=set)
  count: Optional[int] = None
  
  def __repr__(self):
    buff = []
    if self.not_in_word:
      buff.append("Not in word")
    else:
      if self.in_position:
        buff.append("In position: %s" % ", ".join(str(i) for i in self.in_position))
      if self.not_in_position:
        buff.append("Not in position: %s" % ", ".join(str(i) for i in self.not_in_position))
      if self.count:
        buff.append("Count: %s" % self.count)
    return " | ".join(buff)
    
  

class WordleWiz:
  """A class to solve wordle."""
  
  def __init__(self, all_words: Set[str], used_words: Optional[Set[str]] = None):
    """Load word list(s) from file(s)."""
    if not all_words:
      raise WordleWizError("Words list is empty")
    words_len = set(len(word) for word in all_words)
    if len(words_len) > 1:
      raise WordleWizError("Not all words are of the same length %s", words_len)
    self.word_len = words_len.pop()
    if self.word_len > MAX_WORD_LEN:
      raise WordleWizError("Word length of {length} is too long".format(length=self.word_len))
    self.words = frozenset(all_words)
    if used_words:
      self.used_words = frozenset(used_words)
    else:
      self.used_words = frozenset()
    self.reset()
    
  @property
  def knowladge(self):
    if not self._knowladge:
      return "No Data"
    return "\n".join("{c}: {k}".format(c=c, k=self._knowladge[c])
                     for c in sorted(self._knowladge))
                     
  @property
  def population(self):
    if not self._population:
      return "No Data"
    return "\n".join("{c}: {p}".format(c=c, p=self._population[c])
                     for c in sorted(self._population))
                     
  @property
  def scores(self):
    if not self._scores:
      return "No Data"
    return "\n".join("{w}: {s}".format(w=w, s=round(100 * s, 2))
                     for w, s in sorted(self._scores.items(), key=lambda ws: ws[1], reverse=True))
          
  def reset(self):
    """Start from the beginning."""
    self.possible_words = tuple(sorted(self.words))
    self.num_possible = len(self.possible_words)
    self._knowladge = collections.defaultdict(Knowladge)
    self._population = None
    self._scores = None
    
  def run_cycle(self, strict: bool = True) -> str:
    """Run a single cycle and return the best word to use."""
    self._population = self._get_population()
    self._scores = self._score_words(self._population, strict)
    return max(self._scores.items(), key=lambda s: s[1])[0]
    
  def input_result(self, word: str, result: str) -> None:
    """Feed-back results of a word."""
    if len(result) != len(word):
      raise WordleWizError("Result of wrong size")
    for c in result:
      if c not in POSSIBLE_RESULT_CHARS:
        raise WordleWizError("Result is malformed")
    # Add all data
    for i, c in enumerate(word):
      r = ResultChars(result[i])
      if r == ResultChars.NOT_IN_WORD:
        self._knowladge[c].not_in_word = True
      elif r == ResultChars.IN_POSITION:
        self._knowladge[c].in_position.add(i)
      elif r == ResultChars.IN_WORD:
        self._knowladge[c].not_in_position.add(i)
    # Fix or raise on contredictions.
    for c in set(word):
      if self._knowladge[c].in_position or self._knowladge[c].not_in_position:
        if self._knowladge[c].not_in_word:
          count = len([  # If 'c' has both in and not in word, we know its count.
              i for i in range(len(word))
              if word[i] == c and ResultChars(result[i]) != ResultChars.NOT_IN_WORD])
          if self._knowladge[c].count and self._knowladge[c].count != count:
            raise WordleWizError(
                "Contredicting result: Count of letter '{char}' was {count1}, now it is {count2}"
                .format(char=c, count1=self._knowladge[c].coun, count2=count))
          self._knowladge[c].count = count
          self._knowladge[c].not_in_word = False
        if self._knowladge[c].in_position & self._knowladge[c].not_in_position:
          raise WordleWizError(
              "Contredicting result: '{char}' is both in and not in position {pos}"
              .format(char=c,
                      pos=self._knowladge[c].in_position & self._knowladge[c].not_in_position))
    self._filter_possibilities()
    
  def is_word(self, word) -> bool:
    return word in self.words
    
  def get_score(self, word: str) -> int:
    if not self._scores:
      return 0
    return round(100 * self._scores.get(word, 0), 2)
          
  def _filter_possibilities(self) -> None:
    """Filter possible words based on new knowladge."""
    self.possible_words = tuple(word for word in self.possible_words if self._valid_word(word))
    self.num_possible = len(self.possible_words)
    
  def _valid_word(self, word) -> bool:
    """Is a word valid according to our knowladge?"""
    letters_counter = collections.Counter(word)
    for i, c in enumerate(word):
      if c not in self._knowladge:
        continue
      if self._knowladge[c].not_in_word:
        return False
      if i in self._knowladge[c].not_in_position:
        return False
      if self._knowladge[c].count and letters_counter[c] != self._knowladge[c].count:
        return False
    for c, k in self._knowladge.items():
      for i in k.in_position:
        if word[i] != c:
          return False
      if k.not_in_position and c not in word:
        return False
    return True
  
  def _get_population(self) -> Dict[str, Population]:
    """Calculate and return population of letters in all words."""
    population = collections.defaultdict(Population)
    for word in self.possible_words:
      for i, c in enumerate(word):
        population[c].position_count[i] += 1
      for c in set(word):
        population[c].word_count += 1
    return population
        
  def _score_words(self, population: Dict[str, Population], strict: bool) -> Dict[str, float]:
    """Score all possible words, or all words if not strict."""
    return {word: self._score(word, population)
            for word in (self.possible_words if strict else self.words)}
    
  def _score(self, word, population: Dict[str, Population]) -> float:
    """Score a word."""
    # Score is a combination of probelability of an event multiply by the reletive possibilities
    # reduction. Max reduction is into a single possible word. Each letter has three events
    # (results), not-in-word, exact-position, and not-exact-position.
    # (Population / Total) * ((T - P) / (T - 1))
    # P / T -- Probability.
    # T - P -- Reduction.
    # T - 1 -- Max reduction.
    # To combine the scores we multiply the inverses and invert the result.
    # This is as for unrelated probabilities, and it will skew the result when we have a low
    # number of possible words because the scores for each letter will not be unrelated to each
    # other.
    if self.num_possible == 1:
      return 1
    scores = []
    # Not in word (omit double+ letters)
    for c in set(word):
      scores.append(
          self._calculate_score(self.num_possible - population[c].word_count, self.num_possible))
    for i, c in enumerate(word):
      # In  the exact position.
      scores.append(self._calculate_score(population[c].position_count[i], self.num_possible))
      # In word but in other positions (words wil double letters will get skewed).
      scores.append(
          self._calculate_score(
              population[c].word_count - population[c].position_count[i], self.num_possible))
    # Probablity that this is the word we look for.
    if word in self.used_words:
      scores.append(self._calculate_score(1, self.num_possible))
    return self._combine_scores(scores)
    
  @classmethod
  def _calculate_score(cls, p: int, t: int) -> float:
    return (float(p) / t) * (float(t - p) / (t - 1))
    
  def _combine_scores(cls, scores: float) -> float:
    return 1 - functools.reduce(operator.mul, (1 - s for s in scores), 1)
  