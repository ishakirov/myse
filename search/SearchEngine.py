import json
import redis
from stemming.porter2 import stem

class SearchEngine:

    availableOperations = ['&', '|', '!']

    def __init__(self):
        self.redisClient = redis.StrictRedis(host='localhost', port=6379, db=0)

    def boolSearch(self, query):
        stemmedQuery = self.getStemmedQuery(query)
        stemmedQuery = self.infixToRpn(stemmedQuery)
        allDocs = []
        if stemmedQuery.find('!') != -1:
            allDocs = map(lambda x: x.split(':')[1], self.redisClient.keys('parsed_document:*'))

        stack = []
        for val in stemmedQuery.split(' '):
            if val in self.availableOperations:
                if val == '&':
                    op1 = stack.pop()
                    op2 = stack.pop()
                    stack.append(list(set(op1) & set(op2)))
                if val == '|':
                    op1 = stack.pop()
                    op2 = stack.pop()
                    stack.append(list(set(op1+op2)))
                if val == '!':
                    op1 = stack.pop()
                    new_list = list(allDocs)
                    for x in op1:
                        new_list.remove(x)
                    stack.append(new_list)

            else:
                stack.append(list(self.redisClient.smembers('words:{0}'.format(val))))

        return stack.pop()


    def getStemmedQuery(self, query):
        tokens = query.split(' ')
        stemmedQuery = ''
        for token in tokens:
            if not token in self.availableOperations:
                stemmedQuery += stem(token) + ' '
            else:
                stemmedQuery += token + ' '
        return stemmedQuery[:-1]

    def infixToRpn(self, query):
        out = ''
        stack = []
        prec = {
            '!': 2,
            '&': 1,
            '|': 0
        }
        for token in query.split(' '):
            if token in self.availableOperations:
                while stack and prec[stack[-1]] >= prec[token]:
                    out+=stack.pop() + ' '
                stack.append(token)
            else:
                out += token + ' '

        while stack:
            out += stack.pop() + ' '

        return out[:-1]

    def metaSearch(self, author):
        key = 'myse:authors:%s' % author
        return list(self.redisClient.smembers(key))

    def getAuthors(self, mask):
        return map(lambda x: x.split(':')[2].decode('utf-8'), list(self.redisClient.keys('myse:authors:%s*' % mask)))

    def tfidfSearch(self, keyword):
        tf = self.redisClient.smembers('words:tf:%s' % keyword)
        tfDict = {}
        for doc in tf:
            docId = doc.split(':')[0]
            tfVal = float(doc.split(':')[1])
            tfDict[docId] = tfVal

        idf = float(self.redisClient.get('myse:idf:%s' % keyword))

        for k in tfDict:
            tfDict[k] *= idf

        re = []
        for k in tfDict:
            if tfDict[k] > 0.2:
                re.append((k, tfDict[k]))

        re = sorted(re, key=lambda tup: -tup[1])

        return re
