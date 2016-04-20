from django.core.management.base import BaseCommand

import json
import re
import redis
import html2text
from stemming.porter2 import stem
from nltk.corpus import stopwords
import math

class Command(BaseCommand):
    help = 'Compute idf'

    redis = None

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        wordKeys = self.redis.keys('words:*')
        documentCount = len(self.redis.keys('raw_documents:*'))
        self.stdout.write('Total {0} keys'.format(len(wordKeys)))
        i = 0
        for key in wordKeys:
            if key.startswith('words:tf:'):
                continue
            word = key.split(':')[1]
            numDocs = len(self.redis.smembers(key))
            newKey = 'myse:idf:%s' % word
            self.redis.set(newKey, math.log(documentCount / float(numDocs)))
            i += 1
            if i % 100 == 0:
                self.stdout.write('%d of %d...' % (i, len(wordKeys)))


        self.stdout.write('Finished')
