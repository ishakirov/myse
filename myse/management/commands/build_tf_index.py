from django.core.management.base import BaseCommand

import json
import re
import redis
import html2text
from stemming.porter2 import stem
from nltk.corpus import stopwords
import math

class Command(BaseCommand):
    help = 'Build tf index for words'

    redis = None

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        tfDocumentsKeys = self.redis.keys('myse:tf:*')
        self.stdout.write('Total {0} keys'.format(len(tfDocumentsKeys)))
        i = 0
        for key in tfDocumentsKeys:
            docId = key.split(':')[2]
            tf = json.loads(self.redis.get(key))
            for word in tf:
                val = '%s:%f' % (docId, tf[word])
                newKey = 'words:tf:%s' % word
                self.redis.sadd(newKey, val)
            i += 1
            if i % 100 == 0:
                self.stdout.write('%d of %d...' % (i, len(tfDocumentsKeys)))


        self.stdout.write('Finished')
