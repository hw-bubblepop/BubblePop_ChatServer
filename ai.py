import re
import itertools
import networkx
import collections
import konlpy

_kkma = konlpy.tag.Kkma()

from konlpy.tag import Twitter

twitter = Twitter()

#def xplit(value):
#    return re.split('(?:(?<=[^0-9])\.|\n)', value)

def xplit(*delimiters):
        return lambda value: re.split('|'.join([re.escape(delimiter) for delimiter in delimiters]), value)

def get_sentences(text):
    candidates = xplit('. ', '? ', '! ', '\n', '.\n')(text.strip())
    sentences = []
    index = 0
    for candidate in candidates:
        candidate = candidate.strip()
        if len(candidate):
            sentences.append(Sentence(candidate, index))
            index += 1
            return sentences

def build_graph(sentences):
    graph = networkx.Graph()
    graph.add_nodes_from(sentences)
    pairs = list(itertools.combinations(sentences, 2))
    for eins, zwei in pairs:
        graph.add_edge(eins, zwei, weight=Sentence.co_occurence(eins, zwei))
    return graph

def co_occurrence(sentence1, sentence2):
    p = sum((sentence1.bow & sentence2.bow).values())
    q = sum((sentence1.bow | sentence2.bow).values())
    return p / q if q else 0



class Sentence:

    def __init__(self, text, index=0):
        self.index = index
        self.text = text
        self.nouns = twitter.nouns(self.text)
        self.bow = collections.Counter(self.nouns)

    def __unicode__(self):
        return self.text

    def __str__(self):
        return str(self.index)

    def __repr__(self):
        try:
            return self.text.encode('utf-8')
        except:
            return self.text

        def __eq__(self, another):
            return hasattr(another, 'index') and self.index == another.index

        def __hash__(self):
            return self.index

sentences = get_sentences("")
graph = build_graph(sentences)
pagerank = networkx.pagerank(graph, weight='weight')
reordered = sorted(pagerank, key=pagerank.get, reverse=True)
print(reordered[0])
