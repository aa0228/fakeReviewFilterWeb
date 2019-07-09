from os import path
from datetime import datetime
from traceback import print_exc
from .dbSession import dbSession as Session
from .reviewModels import (Review, ReviewUser, ProductType, Product)
from ..coreAlgorithm.textAnalyzer import TextAnalysisMaxSSaver


class LoadReviewDataFromFileToDB:
    __valueMap = {'product/productId': 'productId',
                  'product/title': 'productTitle',
                  'product/price': 'productPrice',
                  'review/userId': 'reviewUserId',
                  'review/profileName': 'reviewUserName',
                  'review/helpfulness': 'reviewDoLikeCount',
                  'review/score': 'reviewScore',
                  'review/time': 'reviewTime',
                  'review/summary': 'reviewSummary',
                  'review/text': 'reviewContent'}
    __linesCount = 10

    def __init__(self, filepath, productTypeName=None):
        assert path.exists(filepath), "{} doesn't exists!".format(filepath)
        self.__filepath = filepath
        self.__addedUserIdSet = set()
        self.__addedProductIdSet = set()
        self.__productTypeId = None
        self.__productTypeName = productTypeName

    def __retriveDataFromLinesAndStoreToDB(self, session, lines):
        '''

        lines are like this:
        product/productId: B002BNZ2XE
        product/title: in
        product/price: 0.00
        review/userId: A2Z8GGXKF1W48Y
        review/profileName: Everlong Gone
        review/helpfulness: 3/3
        review/score: 4.0
        review/time: 1202428800
        review/summary: Jack Wagner Rocks
        review/text: 1


        '''
        data = {}
        for line in lines:
            key, value = line.split(': ', 1)
            assert key in LoadReviewDataFromFileToDB.__valueMap, key
            key = LoadReviewDataFromFileToDB.__valueMap[key]
            data[key] = value

        if data['reviewUserId'] not in self.__addedUserIdSet:
            user = ReviewUser()
            user.id = data['reviewUserId']
            user.name = data['reviewUserName']
            if not user.checkExists(session):
                session.add(user)

        if data['productId'] not in self.__addedProductIdSet:
            product = Product()
            product.id = data['productId']
            product.name = data['productTitle']

            # price可能显示为unknown，所以防止不能转化为float时，要指定一个值
            try:
                product.price = float(data['productPrice'])
            except:
                product.price = -1
            product.productTypeId = self.__productTypeId
            if not product.checkExists(session):
                session.add(product)

        review = Review()
        review.productTypeId = self.__productTypeId
        review.productId = data['productId']
        review.reviewUserId = data['reviewUserId']
        likeCount, totalCount = (int(x) for x in
                                 data['reviewDoLikeCount'].split('/'))
        review.reviewUsefulCount = likeCount
        review.reviewVotedTotalCount = totalCount
        review.reviewTime = datetime.utcfromtimestamp(int(data['reviewTime']))
        review.reviewScore = data['reviewScore']
        review.reviewSummary = data['reviewSummary']
        review.reviewContent = data['reviewContent']
        session.add(review)

    def loadReviewDataFromFileToDB(self):
        productType = ProductType()
        if self.__productTypeName is None:
            index = self.__filepath.rfind('/')
            self.__productTypeName = self.__filepath[index + 1:].split('.')[0]
        productType.name = self.__productTypeName
        session = Session()
        session.add(productType)
        # 必需commit，才能知道productTypeId
        session.commit()
        self.__productTypeId = productType.id

        with open(self.__filepath, 'r') as file:
            canContinue = True
            count = 0
            while canContinue:
                count += 1
                print(count)
                # readlines 并不会返回指定行数，不知道为什么（这里感觉有点坑
                # lines = file.readlines(LoadReviewDataFromFileToDB.\
                # __linesCount)
                lines = [file.readline().rstrip('\n') for i in
                         range(LoadReviewDataFromFileToDB.__linesCount)]
                if not all(lines):
                    print("there's something with lines :{}".format(lines))
                    break
                self.__retriveDataFromLinesAndStoreToDB(session, lines)
                canContinue = file.readline()

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print_exc(e)
            raise e
        finally:
            session.close()

        # 更新textAnalysis中的最大值
        textAnalysisMaxSSaver = TextAnalysisMaxSSaver()
        textAnalysisMaxSSaver.addAnProductTypeId(self.__productTypeId)
        textAnalysisMaxSSaver._saveData()


def loadFileToDatabase(filepaths):
    for filepath in filepaths:
        LoadReviewDataFromFileToDB(filepath).loadReviewDataFromFileToDB()
