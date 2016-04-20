from django.core.management.base import BaseCommand

import redis
import json

class Command(BaseCommand):
    help = 'Builds an index by authors'

    redis = None

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        documentKeys = self.redis.keys('raw_documents:*')
        self.stdout.write('Total {0} keys'.format(len(documentKeys)))
        i = 0
        for key in documentKeys:
            document = eval(self.redis.get(key)) #UNSAFE REMOVE IT PLEASE
            author = document['owner']['display_name']
            docId = key.split(':')[1]
            newKey = 'myse:authors:%s' % author
            self.redis.sadd(newKey, docId)
            i += 1
            if i % 100 == 0:
                self.stdout.write('%d...' % i)

        self.stdout.write('Finished')
