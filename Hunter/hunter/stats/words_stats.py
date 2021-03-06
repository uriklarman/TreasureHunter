from datetime import datetime
from hunter.dictionary.dictionaries import resources_path

__author__ = 'uriklarman'
import cPickle as pickle
from datetime import datetime

stats_dir_path = resources_path + 'stats/'

class WordsStats:
    def __init__(self, config, tweet_file, collected_words):
        self.config = config
        self.tweet_file = tweet_file
        self.collected_words = collected_words
        self.encoding_flow = []

        self.filename = 'stats_%d_%d_%d_%d_%d_%s_%s.pkl'%(config.d, config.l, config.f, config.x, config.shuffle_keywords_seed, tweet_file, str(datetime.now()))
        print 'stats file name is: ', self.filename

    def update(self, link_i, link, link_found, words, threshold, essence, uncut_essence):
        self.__update_encoding_flow(link_i, link, link_found, words, threshold, essence, uncut_essence)
        self.save_stats()

    def __update_encoding_flow(self, link_i, link, link_found, words, threshold, essence, uncut_essence):
        words_set = set(words)
        essence_set = set(essence)
        uncut_essence_set = set(uncut_essence)
        words_in_essence = words_set.intersection(essence_set)
        words_in_uncut_essence = words_set.intersection(uncut_essence_set)

        steps = len(self.collected_words)-1
        forward_steps = len([t for t in self.collected_words if t[0][0] != t[0][1]])
        sidesteps = steps - forward_steps
        if words[0] == words[1]:
            step_kind = "sidestep"
        else:
            step_kind = "forward"

        encoding_flow_item = [steps, link_i, link_found, step_kind, len(words_set), len(words_in_essence),
                              len(words_in_uncut_essence), len(uncut_essence), forward_steps, sidesteps, words,
                              essence, uncut_essence, link, str(datetime.now())]
        print 'encoding_flow_item: %s' % encoding_flow_item

        self.encoding_flow.append(encoding_flow_item)

    def save_stats(self):
        with open(stats_dir_path + self.filename, 'w') as f:
            pickle.dump(self, f)


def load_stats(file_path, path=None):
    if not path:
        path = stats_dir_path
    with open(path + file_path, 'r') as f:
            stats = pickle.load(f)
    return stats

def print_stats(stats_filename, times_per_forward_word, stats_per_forward_word):
    run_stats = load_stats(stats_filename)
    print stats_filename
    print run_stats.encoding_flow[-1]
    steps_of_change = [run_stats.encoding_flow[i] for i in range(len(run_stats.encoding_flow)-1) if run_stats.encoding_flow[i][0] != run_stats.encoding_flow[i+1][0]]

    important_stats = [x[:2] + x[3:4] + [datetime.strptime(x[-1], '%Y-%m-%d %H:%M:%S.%f')] for x in steps_of_change]

    forwards = important_stats[:1] + [x for x in important_stats if x[2] == 'forward']
    times_per_forward_word.append([x[3] for x in forwards])
    stats_per_forward_word.append(forwards)

    # date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    #
    # steps_of_success = [run_stats.encoding_flow[i] for i in range(len(run_stats.encoding_flow)-1) if run_stats.encoding_flow[i][0] < run_stats.encoding_flow[i+1][0]]
    # steps_of_success_full = [x for x in steps_of_success if x[4] == run_stats.config.w]
    #
    # steps_of_backtrace = [run_stats.encoding_flow[i] for i in range(len(run_stats.encoding_flow)-1) if run_stats.encoding_flow[i][0] > run_stats.encoding_flow[i+1][0]]
    # steps_of_backtrace_full = [x for x in steps_of_backtrace if x[4] == run_stats.config.w]
    #
    # backtrace_success_ratio = float(len(steps_of_backtrace)) / len(steps_of_success)
    # backtrace_success_ratio_full =  float(len(steps_of_backtrace_full)) / len(steps_of_success_full)
    #
    # uncut_essences = [x[7] for x in run_stats.encoding_flow]
    #
    # steps_with_potential_to_succeed = [x for x in run_stats.encoding_flow if x[4] == x[6]]
    # potential_ratio = float(len(steps_with_potential_to_succeed)) / len(run_stats.encoding_flow)
    #
    # print run_stats