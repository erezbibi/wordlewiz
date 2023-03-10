"""WordleWiz banchmark test."""
import statistics
import sys
import wizlib
import ww_utils

START_WORD = "irate"  # A shortcut


def play(word: str, ww: wizlib.WordleWiz):
  """Play one game and return the number of rounds played."""
  ww.reset()
  round_count = 0
  selected_word = START_WORD
  result = None
  while not ww_utils.got_it(result):
    result = ww_utils.get_result(selected_word, word)
    ww.input_result(selected_word, result)
    selected_word = ww.run_cycle(ww.num_possible < ww_utils.NOT_STRICT_LIMIT)
    round_count += 1
  return round_count


if __name__ == "__main__":
  ww = wizlib.WordleWiz(ww_utils.read_words(ww_utils.USED_WORDS_FILE),
                        ww_utils.read_words(ww_utils.USED_WORDS_FILE))
  stats = {}
  total = len(ww.used_words)
  for count, word in enumerate(list(ww.used_words)):
    stats[word] = play(word, ww)
    sys.stdout.write("\r{done}/{total}   ".format(done=count, total=total))
  print("\nStats:")
  print("Avg:", round(statistics.mean(stats.values()), 3))
  print("Stdv:", round(statistics.pstdev(stats.values()), 3))
  print("Max:", max(stats.items(), key=lambda i: i[1]))
  print("Min:", min((r for r in stats.items() if r), key=lambda i: i[1]))
  