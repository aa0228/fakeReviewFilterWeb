import numpy as np
import gc
from collections import defaultdict
from os import path
from .dataSaver import DataSaver
from ..infoDatabase.reviewModels import Review, ProductType
from ..infoDatabase.dbSession import dbSession as Session
from ..infoDatabase.pymysqlConfig import pymysqlConfig
from pymysql import Connect
from concurrent import futures
from multiprocessing import cpu_count


def splitStringToWord(string):
    return string.split()


def loadStopWordsFromFile(filepath):
    stopWordSet = set()
    with open(filepath, 'r') as file:
        for line in file:
            stopWordSet.add(line)
    return stopWordSet


class TextAnalyzer:
    """

    计算某用户对某种商品的评论文本相似度得分

    """
    def __init__(self, docs, typeId, stopWordSet=None):
        self.docs = docs
        self.typeId = typeId
        self.stopWordSet = stopWordSet if stopWordSet is not None else set()
        self.parseDocs()

    def parseDocs(self):
        '''

        将文档转化成词的字典的列表 除去停用词集合
        返回 [{word: wordCount, ...}, ...]

        '''
        self.parsedDocs = []
        for doc in self.docs:
            parsedDoc = defaultdict(int)
            for word in filter(lambda word: word not in self.stopWordSet,
                               splitStringToWord(doc)):
                parsedDoc[word] += 1
            self.parsedDocs.append(parsedDoc)

    def convertToVecs(self):
        '''

        返回针对每个doc的特征词向量

        '''
        # words即为特征词
        words = list(set(word for parsedDoc in self.parsedDocs
                         for word in parsedDoc))
        totalDocCount = len(self.parsedDocs)
        res = []
        for parsedDoc in self.parsedDocs:
            docWordCount = sum(parsedDoc.values())
            vec = np.zeros(len(words), np.float64)
            for i, word in enumerate(words):
                if word not in parsedDoc:
                    continue

                tf = parsedDoc[word] / docWordCount
                occuredDocCount = 1
                for parsedDoc in self.parsedDocs:
                    if word in parsedDoc:
                        occuredDocCount += 1
                idf = totalDocCount / occuredDocCount
                tfIdf = tf * idf
                vec[i] = tfIdf

            res.append(vec)
        return res

    def computeSimsOfTwoVec(self, lhs, rhs):
        '''

        返回 两个向量的空间夹角的余弦值
        lhs, rhs 必需为numpy的向量

        '''
        x = lhs.dot(rhs)
        lhsLen = lhs.dot(lhs)
        rhsLen = rhs.dot(rhs)
        return (x * x) / (lhsLen * rhsLen)

    def getAvgSim(self):
        '''

        获得这些文档的平均相似度

        '''
        vecs = self.convertToVecs()
        simSum = 0
        count = 0
        for i in range(len(vecs) - 1):
            for j in range(i + 1, len(vecs)):
                simSum = self.computeSimsOfTwoVec(vecs[i], vecs[j])
                count += 1
        if count:
            return float(simSum / count)
        # 当没有时为零
        return 0

    def getS(self):
        return len(self.docs) * self.getAvgSim()

    def getSimGrade(self):
        maxSSaver = TextAnalysisMaxSSaver()
        S = self.getS()
        if S > maxSSaver.getData(self.typeId):
            maxSSaver.setData(self.typeId, S)
        return S / maxSSaver.getData(self.typeId)


class TextAnalysisMaxSSaver2(DataSaver):
    """

    保存每类商品评论文本相似度的最大值

    """
    saveFilePath = './savedData/textAnalysisSavedData'

    def _initMaxSData(self):
        session = Session()
        try:
            res = session.query(ProductType.id).all()
            productTypeIds = [row[0] for row in res]
        finally:
            session.close()

        self._data = {}
        for productTypeId in productTypeIds:
            maxS = self._getMaxSOfAProductType(productTypeId)
            if maxS is not None:
                self._data[productTypeId] = maxS

    def __init__(self):
        super(TextAnalysisMaxSSaver, self).__init__(self.saveFilePath)
        if path.exists(self.saveFilePath):
            self._loadDataFromFile()
        else:
            self._initMaxSData()
            self._saveDataToFile()

    def _getMaxSOfAProductType(self, productTypeId):
        session = Session()
        try:
            maxS = float('-inf')
            res = (session.query(Review.reviewUserId).
                   filter(Review.productTypeId == productTypeId).
                   distinct().all())
            userIds = [row[0] for row in res]
            for userId in userIds:
                res = (session.query(Review.reviewContent).
                       filter(Review.reviewUserId == userId and
                              Review.productTypeId == productTypeId).all())
                contents = [row[0] for row in res]
                S = TextAnalyzer(contents, productTypeId).getS()
                maxS = max(maxS, S)
            return maxS if maxS != float('-inf') else None
        finally:
            session.close()

    def addAnProductTypeId(self, productTypeId):
        if productTypeId in self._data:
            return
        maxS = self._getMaxSOfAProductType(productTypeId)
        self._data[productTypeId] = maxS


class TextAnalysisMaxSSaver:
    """

    将maxS保存在数据库中

    """
    def _initMaxSData(self):
        getMaxSRecordsSql = 'select productTypeId, maxS from\
        textAnalysisMaxSRecord;'

        getProductTypeIdsSql = 'select id from productType where id not in \
        (select productTypeId from textAnalysisMaxSRecord);'
        connection = Connect(**pymysqlConfig)
        try:
            with connection as cursor:
                # 载入已经计算好了的maxS
                cursor.execute(getMaxSRecordsSql)
                res = cursor.fetchall()
                self._data = {row[0]: row[1] for row in res}

                # 初始化为计算的
                cursor.execute(getProductTypeIdsSql)
                res = cursor.fetchall()
                for productTypeId in (row[0] for row in res):
                    maxS = self._getMaxSOfAProductType(productTypeId)
                    if maxS is not None:
                        self._data[productTypeId] = maxS
        finally:
            connection.close()

    def __init__(self):
        self._getMaxSOfAProductType = self._getMaxSOfAProductTypeParallel
        self._initMaxSData()

    def _getMaxSOfAProductTypeSingle(self, productTypeId):
        getUserIdsSql = 'select reviewUserId from review \
        where productTypeId = %s;'
        connection = Connect(**pymysqlConfig)
        try:
            maxS = float('-inf')
            with connection as cursor:
                cursor.execute(getUserIdsSql, (productTypeId, ))
                for userId in (row[0] for row in cursor.fetchall()):
                    S = self._computeSOfAUserInAProductType(connection,
                                                            userId,
                                                            productTypeId)
                    maxS = max(maxS, S)
                return maxS if maxS != float('-inf') else None
        finally:
            connection.close()

    def _getMaxSOfAProductTypeParallel(self, productTypeId, processCount=None):
        getUserIdsSql = 'select reviewUserId from review \
        where productTypeid = %s;'
        connection = Connect(**pymysqlConfig)
        processCount = (processCount
                        if processCount is not None else cpu_count())
        try:
            maxS = float('-inf')
            with connection as cursor:
                cursor.execute(getUserIdsSql, (productTypeId, ))
                userIds = [row[0] for row in cursor.fetchall()]
                perCount = len(userIds) // processCount
                userIdParts = [userIds[i * perCount: (i + 1) * perCount]
                               for i in range(processCount - 1)]
                userIdParts.append(userIds[(processCount - 1) * perCount:])

                with futures.ProcessPoolExecutor(
                        max_workers=processCount) as pool:
                    results = [pool.submit(self._computeMaxSOfSomeUserInAProductType,
                                           userIds, productTypeId)
                               for userIds in userIdParts]
                    for future in futures.as_completed(results):
                        maxS = max(maxS, future.result())
                    return maxS if maxS != float('-inf') else None
        finally:
            connection.close()

    def _computeMaxSOfSomeUserInAProductType(self, userIds, productTypeId):
        connection = Connect(**pymysqlConfig)
        try:
            maxS = float('-inf')
            count = 0
            for userId in userIds:
                S = self._computeSOfAUserInAProductType(connection,
                                                        userId,
                                                        productTypeId)
                maxS = max(maxS, S)
                count += 1
                if count % 5 == 0:
                    gc.collect()
            return maxS
        finally:
            connection.close()

    def _computeSOfAUserInAProductType(self, connection, userId,
                                       productTypeId):
        getReviewsOfAUserSql = 'select reviewContent from review \
        where reviewUserId = %s and productTypeId = %s;'
        with connection as cursor:
            cursor.execute(getReviewsOfAUserSql, (userId, productTypeId))
            contents = [row[0] for row in cursor.fetchall()]
            return TextAnalyzer(contents, productTypeId).getS()

    def addAnProductTypeId(self, productTypeId):
        if productTypeId in self._data:
            return
        maxS = self._getMaxSOfAProductType(productTypeId)
        self._data[productTypeId] = maxS

    def getData(self, key):
        return self._data[key]

    def setData(self, key, value):
        self._data[key] = value

    def __enter__(self):
        return self

    def __exit__(self, excType, excValue, traceback):
        self._saveData()

    def _saveData(self):
        """

        保存数据

        """
        getExistIdSql = 'select productTypeId from textAnalysisMaxSRecord;'
        insertSql = 'insert into textAnalysisMaxSRecord(productTypeId, maxS) \
        values(%s, %s);'
        updateSql = 'update textAnalysisMaxSRecord set maxS = %s\
        where id = %s;'
        connection = Connect(**pymysqlConfig)
        try:
            with connection as cursor:
                cursor.execute(getExistIdSql)
                existsIds = set(row[0] for row in cursor.fetchall())
                insertPairs = []
                changePairs = []
                for productTypeId, maxS in self._data.items():
                    if productTypeId in existsIds:
                        changePairs.append((maxS, productTypeId))
                    else:
                        insertPairs.append((productTypeId, maxS))
                cursor.executemany(insertSql, insertPairs)
                cursor.executemany(updateSql, changePairs)
        finally:
            connection.close()
