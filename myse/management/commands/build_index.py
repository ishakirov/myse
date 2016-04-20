from django.core.management.base import BaseCommand

import redis

class Command(BaseCommand):
    help = 'Builds an inverted index'

    redis = None

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        documentKeys = self.redis.keys('parsed_document:*')
        self.stdout.write('Total {0} keys'.format(len(documentKeys)))
        i = 0
        for key in documentKeys:
            document = eval(self.redis.get(key)) #UNSAFE REMOVE IT PLEASE
            documentId = key.split(':')[1]
            for word in document['words']:
                wordKey = 'words:{0}'.format(word)
                self.redis.sadd(wordKey, documentId)
            i += 1
            if i % 100 == 0:
                self.stdout.write('Processed {0} documents...'.format(i))
        self.stdout.write('Finished')
