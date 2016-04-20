from django.core.management.base import BaseCommand

import json
import re
import redis
import html2text
from stemming.porter2 import stem
from nltk.corpus import stopwords

class Command(BaseCommand):
    help = 'Parse raw documents'

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
            newDocument = self.processDocument(key)
            newKey = 'parsed_document:{0}'.format(key.split(':')[1])
            self.redis.set(newKey, newDocument)
            self.documentCount += 1
            if self.documentCount % 100 == 0:
                self.stdout.write('Processed {0} documents...'.format(self.documentCount))

        self.stdout.write('Finished')

    def getKeys(self):
        return self.redis.keys('raw_documents:*')

    def processDocument(self, key):
        document = eval(self.redis.get(key)) #UNSAFE REMOVE IT PLEASE
        newDocument = {}
        newDocument['tags'] = document['tags']
        newDocument['words'] = self.processText(document['title'] + ' ' + document['body'])

        return newDocument

    def processText(self, text):
        textWithoutCode = re.sub(r'<code>.*<\/code>', '', text)
        textWithoutHtml = self.html2text.handle(textWithoutCode)
        cleanText = re.sub('\\n', ' ', textWithoutHtml)
        cleanText = re.sub(r'[^a-zA-Z0-9\s]+', '', cleanText).lower().strip()
        ret = []
        for word in cleanText.split(' '):
            if word != '' and word != '\n' and len(word) > 1:
                ret.append(stem(word))

        sret = set(ret)
        lret = list(ret)
        filtered_words = [word for word in lret if word not in stopwords.words('english')]



        return filtered_words
