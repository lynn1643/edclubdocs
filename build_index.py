import os, re, json
from collections import defaultdict
from ruamel.yaml import YAML
yaml = YAML(typ='safe')

stop_words = set([ "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves" ])

from HTMLParser import HTMLParser
# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.text_snippets = []
        
    def extract(self):
        res = ' '.join(self.text_snippets)
        self.text_snippets = []
        return res
    
    # def handle_starttag(self, tag, attrs):
    #     print "Encountered a start tag:", tag

    # def handle_endtag(self, tag):
    #     print "Encountered an end tag :", tag

    def handle_data(self, data):
        if len(data) > 2:
            clean_text = re.sub('[^a-z]+', ' ', data.lower())
            self.text_snippets.append(clean_text.strip())
            
parser = MyHTMLParser()

PROJ_DIR = os.path.abspath(os.path.dirname(__file__))
DOCS_DIR = os.path.join(PROJ_DIR, 'docs')
OUTPUT_FILE = os.path.join(PROJ_DIR, 'src', 'index.json')

menu = yaml.load(file(os.path.join(PROJ_DIR, 'src/user-guide.yaml')).read())
docs = {}
def traverse_menu(menu):
    has_active = False
    for item in menu:
        docs[item['path']] = item['name']
        if 'subtopics' in item:
            traverse_menu(item['subtopics'])

traverse_menu(menu)

items = []
tokens = defaultdict(set)
for doc in docs.keys():
    item = {'n': docs[doc], 'p': doc}

    html_content = ''
    with open(os.path.join(DOCS_DIR, item['p']), 'r') as help_file:
        html_content = help_file.read().strip()
    parser.feed(html_content)
    text_content = parser.extract()
    
    if text_content:
        title_content = re.sub('[^a-z]+', ' ', item['n'].lower()).strip()
        text_content += ' ' + title_content
        i = len(items)

        for token in text_content.split(' '):
            if token and not token in stop_words:
                tokens[token].add(i)
        item['s'] = len(text_content)     
        items.append(item)     

relevant_tokens = {}
MAX = 70
for token in tokens:
    idocs = tokens[token]
    if len(idocs) <= MAX:
        # relevant_tokens[token] = ' '.join(map(str, sorted(list(idocs), lambda a,b: -1 if items[a]['s'] < items[b]['s'] else 1)))
        relevant_tokens[token] = ' '.join(map(str, sorted(list(idocs), lambda a,b: -1 if items[a]['s'] < items[b]['s'] else 1)))

index = {'items': items, 'tokens': relevant_tokens}
print "page count:", len(items)
print "index size:", len(json.dumps(index, separators=(',',':')))
print index

with open(OUTPUT_FILE, 'w') as outfile:
    json.dump(index, outfile, separators=(',',':'))