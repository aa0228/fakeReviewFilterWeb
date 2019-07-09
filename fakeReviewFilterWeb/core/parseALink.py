from collections import defaultdict
from .crawler.asyncGetDataByLinkWithAiohttp import asyncGetData
from .infoDatabase.dbSession import dbSession as Session
from .infoDatabase.reviewModels import Review, ProductType
from .coreAlgorithm.scoreAnalyzer import ScoreAnalyzer
from .coreAlgorithm.textAnalyzer import TextAnalyzer
from .coreAlgorithm.emotionAnalyzer import EmotionAnalyzer
from .randomForestModel import RandomForestModel


def getModels():
    session = Session()
    try:
        res = session.query(ProductType.id).all()
        return {productTypeId: RandomForestModel(productTypeId)
                for productTypeId, *_ in res}
    except:
        session.rollback()
        raise
    finally:
        session.close()


models = getModels()


def saveToDatabase(product, users, reviews):
    session = Session()
    try:
        if not product.checkExists():
            session.add(product)
        for user in users:
            if not user.checkExists():
                session.add(user)
        for review in reviews:
            if not review.checkExists():
                session.add(review)
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()


def giveAdvice(fakeRatio):
    if fakeRatio > 0.5:
        return '该商品虚假评论比例较高,不建议购买.'
    elif fakeRatio > 0.3:
        return '该商品存在虚假评论,请谨慎购买'
    else:
        return '该商品虚假评论比例较低.'


def parseALink(url, productTypeId):
    """

    对外接口,对url所指的商品进行分析,返回真实的评论
    并返回平均值

    """
    product, users, reviews = asyncGetData(url, productTypeId)
    saveToDatabase(product, users, reviews)

    session = Session()
    realReviewUsers = {}
    scoreSimCounter = defaultdict(int)
    textSimCounter = defaultdict(int)
    emotionSimCounter = defaultdict(int)
    for user in users:
        res = (session.query(Review.reviewScore, Review.reviewContent).
               filter(Review.reviewUserId == user.id and
                      Review.productTypeId == productTypeId).all())
        scores = [row[0] for row in res]
        scoreSimGrade = ScoreAnalyzer(scores).getGrade()
        scoreSimCounter[scoreSimGrade] += 1

        reviewContents = [row[1] for row in res]
        textSimGrade = TextAnalyzer(reviewContents,
                                    productTypeId).getSimGrade()
        textSimCounter[textSimGrade] += 1

        emotionSimGrade = EmotionAnalyzer(reviewContents).getGrade()
        emotionSimCounter[emotionSimGrade] += 1
        if models[productTypeId].predictOne((scoreSimGrade, textSimGrade,
                                             emotionSimGrade)) == 0:
            realReviewUsers[user.id] = user.name
    data = {}
    data['productName'] = product.name
    data['totalReviewCount'] = len(reviews)

    realReviews = [review for review in reviews
                   if review.reviewUserId in realReviewUsers]
    data['fakeReviewCount'] = len(reviews) - len(realReviews)
    data['advice'] = giveAdvice(1 - len(realReviews) / len(reviews))

    data['scoreSimScoreInfo'] = list(scoreSimCounter.items())
    data['textSimScoreInfo'] = list(textSimCounter.items())
    data['emotionSimScoreInfo'] = list(emotionSimCounter.items())

    realReviews.sort(key=lambda item: item.reviewTime, reverse=True)
    realReviewInfos = [[realReviewUsers[review.reviewUserId],
                        review.reviewTime.strftime('%m/%d/%Y'),
                        review.reviewContent]
                       for review in realReviews]
    data['reviews'] = realReviewInfos
    return data


# argsOfProductType = {}


# def initArgs():
#     sql = 'select productTypeId, scoreRatio, textRatio, emotionRatio, threshold\
#     from argsOfProductType;'
#     connection = Connect(**pymysqlConfig)
#     try:
#         with connection as cursor:
#             cursor.execute(sql)
#             for (productTypeId, scoreR,
#                  textR, emotionR, threshold) in cursor.fetchall():
#                 argsOfProductType[productTypeId] = (scoreR, textR,
#                                                     emotionR, threshold)
#     finally:
#         connection.close()


# initArgs()


# def computeSimGrade(scoreSimGrade, textSimGrade, emotionSimGrade,
#                     productTypeId):
#     scoreR, textR, emotionR, threshold = argsOfProductType[productTypeId]
#     return (scoreSimGrade * scoreR + textSimGrade * textR +
#             emotionSimGrade * emotionR), threshold
