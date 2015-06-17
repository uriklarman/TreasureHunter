import sys
import traceback
from time import sleep
import os
import multiprocessing
import signal
from hunter.dictionary import dictionaries
from multiprocessing import Process
from search.search import Search

from stats.words_stats import WordsStats, print_stats, stats_dir_path
from distillery import Distillery


__author__ = 'uriklarman'

sidestep_threshold = 600
tweets_path = dictionaries.resources_path + 'tweets/'

def timeout_handler(signum, frame):
    print('distillery timed out with signal', signum)
    raise RuntimeError("distillery timed out")

def find_link(words, search_engine, distillery, dicts, stats, threshold=10000):

    links_list, next_url = links_list, next_url = search_engine.new_search(words)
    link_i = 0
    link_found = False
    while link_i < threshold:
        for link in links_list:

            if 'pdf' in link or 'datalounge' in link or 'github' in link or 'ufdc.ufl.edu' in link:
                continue

            link_i += 1
            while True:
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(15)
                    essence, uncut_essence = distillery.distill(link, dicts.keywords)
                    signal.alarm(0)
                    break
                except Exception as inst:
                    print 'Failed to distill. trying again'
                    print(traceback.format_exc())
                    link = "http://google.com"
                    distillery.restart_browser()

            link_found = set(words).issubset(set(essence))
            stats.update(link_i, link, words, threshold, essence, uncut_essence)

            if link_found or link_i >= threshold:
                break
        if link_found or link_i >= threshold:
            break

        if next_url:
            stop_trying = False
            try:
                sleep(1)
                links_list, next_url = search_engine.continuing_search(next_url)
            except Exception as inst:
                print(traceback.format_exc())
                stop_trying = True
        else:
            stop_trying = True

        if stop_trying:
            print '!'*30
            print "Could not continue search. given next_url: '%s'"%(next_url)
            print '!'*30
            link_found, link_i, link, essence = (False, 0, '', [])
            break

    return link_found, link, essence


def conceal_step(data_words, words, search_engine, distillery, dicts, stats):

    link_found, link, essence = find_link(words, search_engine, distillery, dicts, stats, sidestep_threshold)

    if link_found:
        next_words = [data_words.pop()]
    else:
        # save D-word for next attempt, and copy L1-word into D-word
        next_words = [words[0]]
        words[0] = words[1]

        sidestep_found, link, essence = find_link(words, search_engine, distillery, dicts, stats)
        if not sidestep_found:
            print 'oh boy... No link was found for side stepping.'

    if link not in dicts.links:
        links_dict = dictionaries.add_link_to_links_file(link, dicts, config)
    next_words += dicts.links[link]
    next_words += dictionaries.indexes_to_f_keywords([essence.index(w) for w in words], dicts.keywords, config)

    return next_words, link


def conceal(tweet_file, config, endword_index=False):
    dicts = dictionaries.load_dictionaries(config)
    print 'keywords (x) = ', config.x
    print 'Essence len = ', config.essence_len
    distillery = Distillery(config.essence_len, dicts.keywords)
    search_engine = Search()
    raw_data_words = open(tweets_path + tweet_file).read().split()
    data_words = [keyword for word in raw_data_words for keyword in dicts.english["".join(c for c in word.lower() if c not in ('!', '.', ':', ',', '?', '"', '-'))]]

    if endword_index:
        words = [dicts.keywords[endword_index]] * config.w
    else:
        words = [dicts.keywords[config.x - 1]] * config.w

    collected_words = [(words, '')]
    stats = WordsStats(config, tweet_file, collected_words)

    try:
        while True:
            words, link = conceal_step(data_words, words, search_engine, distillery, dicts, stats)
            collected_words.append((words, link))
            if not data_words:
                break

    except Exception:
        print(traceback.format_exc())
        t, v, tb = sys.exc_info()
        distillery.browser.close()
        raise t, v, tb

    print "collected words are: %s" % collected_words
    return collected_words


if __name__ == '__main__':
    # all_files = os.listdir(stats_dir_path)[1:]
    # for filename in all_files:
    #     print_stats(filename)


    # stats_1_2_2_89_10_tweet_CO_1.txt_2015-06-08 10:32:28.329322.pkl
    # [26, 29, False, 'forward', 5, 1, 5, 19, 19, 7, ['par', 'executive', 'oliver', 'inspiration', 'arena'], set(['oliver']), set(['arena', 'oliver', 'par', 'executive', 'inspiration']), 'https://playedtwice.wordpress.com/', '2015-06-08 17:24:31.617210']
    # best_file = 'stats_1_2_2_89_10_tweet_CO_1.txt_2015-06-08 10:32:28.329322.pkl'
    # print_stats(best_file)

    tweet_file = 'tweet_CO_02.txt'
    config = dictionaries.Config(1, 2, 2, 89, 10, 200)

    # dictionaries.create_and_save_dicts(config)
    conceal(tweet_file, config)