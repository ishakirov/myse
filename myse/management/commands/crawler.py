from django.core.management.base import BaseCommand

import gzip
import StringIO
import json
import redis
import urllib

BASE_URL = 'https://api.stackexchange.com/2.2/questions?page={0}&pagesize=100&fromdate=1454284800&todate=1454803200&order=desc&sort=creation&site=stackoverflow&filter=!9YdnSIN18'

class Command(BaseCommand):
    help = 'Crawl the stackexchange'

    redis = None
    questionCount = 0

    def handle(self, *args, **options):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

        pageNumber = 1

        data = self.getJsonData(pageNumber)

        self.saveInRedis(data)

        while data['has_more']:
            pageNumber += 1
            data = self.getJsonData(pageNumber)
            self.saveInRedis(data)
            self.stdout.write('{0}...'.format(self.questionCount))

        self.stdout.write('Finished! {0} questions parsed'.format(self.questionCount))

    def saveInRedis(self, data):
        for question in data['items']:
            key = 'raw_documents:{0}'.format(question['question_id'])
            self.redis.set(key, question)
            self.questionCount += 1

    def getJsonData(self, pageNumber):
        response = urllib.urlopen(BASE_URL.format(pageNumber))
        compresseddata = response.read()
        compressedstream = StringIO.StringIO(compresseddata)
        gzipper = gzip.GzipFile(fileobj=compressedstream)

        return json.loads(gzipper.read())
