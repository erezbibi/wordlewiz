"""Play the wordle game in a CLI."""
import random
import wizlib
import ww_utils


def _get_test_word(ww: wizlib.WordleWiz) -> str:
  """Get a word to play on (to try to find)."""
  test_word = input("Input a word (Enter for interactive, ? for random): ")
  if test_word:
    if test_word == "?":
      test_word = random.choice(list(ww.words))
    if len(test_word) != ww.word_len:
      raise RuntimeError("Wrong word length")
    if test_word not in ww.words:
      raise RuntimeError("Word does not exists")
  return test_word.strip()


def _maybe_overide_selected(selected: str, ww: wizlib.WordleWiz) -> str:
  """Accept best word or override it."""
  while True:
    overide = input("Selected Word: {word} ({score}%) "
                    .format(word=selected, score=ww.get_score(selected)))
    if not overide:
      return selected
    if overide.startswith("?"):
      _handle_info(overide, ww)
      continue
    if ww.is_word(overide):
      print("Selected Word: {word} ({score}%)"
            .format(word=overide, score=ww.get_score(overide)))
      return overide
    print("'%s' is not a word" % overide)
    

def _handle_info(command: str, ww: wizlib.WordleWiz) -> None:
  """Show info."""
  if len(command) > 1:
    c = command[1].upper()
    if c == "W":
      print(ww.possible_words)
      return
    if c == "K":
      print(ww.knowladge)
      return
    if c == "S":
      print(ww.scores)
      return
    if c == "P":
      print(ww.population)
      return
  print("For info type ?W[ord]|K[nowladge]|S[cores]|P[opulation]")
      

if __name__ == "__main__":
  try:
    ww = wizlib.WordleWiz(ww_utils.read_words(ww_utils.ALL_WORDS_FILE),
                          ww_utils.read_words(ww_utils.USED_WORDS_FILE))
    test_word = _get_test_word(ww)
    round_count = 0
    result = None
    print("Selected word: Enter to accept, type to overide, ? for info")
    while not ww_utils.got_it(result):
      round_count += 1
      print("Round:", round_count, "- Num possibilities:", ww.num_possible)
      selected_word = ww.run_cycle(ww.num_possible < ww_utils.NOT_STRICT_LIMIT)
      selected_word = _maybe_overide_selected(selected_word, ww)
      if test_word:
        result = ww_utils.get_result(selected_word, test_word)
        print("       Result:", result)
      else:
        result = input("       Result: ")
      ww.input_result(selected_word, result)
    print("The word is:", selected_word)
  except Exception as e:
    print("Error:", e)
  finally:
    input("\nWe are done.")
