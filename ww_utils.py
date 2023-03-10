"""Common utils."""
import collections
import enum
import string

from typing import Set

ALL_WORDS_FILE = "C:\\Users\\Erez\\WordleWiz\\words"
USED_WORDS_FILE = "C:\\Users\\Erez\\WordleWiz\\valid_words"
NOT_STRICT_LIMIT = 100  # If more that X possiblities, use non-strict mode.
MAX_WORD_LEN = 5
LETTERS = frozenset(string.ascii_lowercase)


class ResultChars(enum.Enum):
  """The three types of results for a letter (black, yellow, green)."""
  NOT_IN_WORD = "-"
  IN_WORD = "*"
  IN_POSITION = "!"
  
POSSIBLE_RESULT_CHARS = {m.value for m in ResultChars.__members__.values()}


def get_result(selected_word, test_word) -> str:
  """Get the results when we know the word we look for."""
  # Assume all is wrong
  result = [ResultChars.NOT_IN_WORD.value] * len(selected_word)
  count_letters = collections.Counter(test_word)
  # Count exact matches
  for i, c in enumerate(selected_word):
    if c == test_word[i]:
      result[i] = ResultChars.IN_POSITION.value
      count_letters[c] -= 1
  # Count non exact matches
  for i, c in enumerate(selected_word):
    if c in test_word and c != test_word[i] and count_letters.get(c, 0) > 0:
      result[i] = ResultChars.IN_WORD.value
      count_letters[c] -= 1
  return "".join(result)


def got_it(result: str):
  return result and all(c == ResultChars.IN_POSITION.value for c in result)
  
 
def read_words(file_path: str) -> Set[str]:
  """Read a word list from file."""
  with open(file_path, mode="rt", encoding="ascii") as fl:
    return frozenset(word.strip() for word in fl)