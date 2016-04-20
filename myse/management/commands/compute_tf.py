from django.core.management.base import BaseCommand

import json
import re
import redis
import html2text
from stemming.porter2 import stem
from nltk.corpus import stopwords

class Command(BaseCommand):
    help = 'Compute tf'

    redis = None
    html2text = None
    regex = None
    documentCount = 0

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = True

        documentKeys = self.getKeys()

        self.stdout.write('Total {0} keys'.format(len(documentKeys)))

        for key in documentKeys:
            tf = self.processDocument(key)
            newKey = 'myse:tf:{0}'.format(key.split(':')[1])
            self.redis.set(newKey, json.dumps(tf))
            self.documentCount += 1
            if self.documentCount % 100 == 0:
                self.stdout.write('Processed {0} documents...'.format(self.documentCount))

        self.stdout.write('Finished')

    def getKeys(self):
        return self.redis.keys('raw_documents:*')

    def processDocument(self, key):
        document = eval(self.redis.get(key)) #UNSAFE REMOVE IT PLEASE
        documentText = document['title'] + ' ' + document['body']
        wordList = self.processText(documentText)
        return self.tf(wordList)

    def processText(self, text):
        textWithoutCode = re.sub(r'<code>.*<\/code>', '', text)
        textWithoutHtml = self.html2text.handle(textWithoutCode)
        cleanText = re.sub('\\n', ' ', textWithoutHtml)
        cleanText = re.sub(r'[^a-zA-Z0-9\s]+', '', cleanText).lower().strip()
        ret = []
        for word in cleanText.split(' '):
            if word != '' and word != '\n' and len(word) > 1:
                ret.append(stem(word))

        filtered_words = [word for word in ret if word not in stopwords.words('english')]

        return filtered_words

    def tf(self, words):
        re = {}

        for word in words:
            if word in re:
                re[word] += 1
            else:
                re[word] = 1

        for k in re:
            re[k] = re[k] / float(len(words))

        return re
