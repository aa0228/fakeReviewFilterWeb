"""

对一类商品生成一个文件
文件的每一行表示:
    在该类商品下,每一个用户的各项的得分

"""


from os import path, mkdir
from fakeReviewFilterWeb.core.coreAlgorithm.textAnalyzer import TextAnalyzer
from fakeReviewFilterWeb.core.coreAlgorithm.emotionAnalyzer \
    import EmotionAnalyzer
from fakeReviewFilterWeb.core.coreAlgorithm.scoreAnalyzer import ScoreAnalyzer
from fakeReviewFilterWeb.core.infoDatabase.dbSession \
    import dbSession as Session
from fakeReviewFilterWeb.core.infoDatabase.reviewModels import (Review,
                                                                ProductType)


class ReviewUserAnalyzer:
    """

    返回某一类商品下,所有用户的各项得分

    """
    def __init__(self, productTypeId):
        self._productTypeId = productTypeId
        self._userIds = None
        self._currentPos = None

    def __iter__(self):
        if self._userIds is None:
            session = Session()
            try:
                res = (session.query(Review.reviewUserId).
                       filter(Review.productTypeId == self._productTypeId).
                       distinct().all())
                self._userIds = [row[0] for row in res]
            finally:
                session.close()
        self._currentPos = 0
        return self

    def __next__(self):
        """

        return 评分相似度得分,文本相似度得分,情感相似度得分

        """
        if self._currentPos >= len(self._userIds):
            raise StopIteration
        userId = self._userIds[self._currentPos]
        self._currentPos += 1

        session = Session()
        try:
            res = (session.query(Review.reviewScore, Review.reviewContent).
                   filter(Review.reviewUserId == userId and
                          Review.productTypeId == self._productTypeId).all())
            scores = [row[0] for row in res]
            scoreSimGrade = ScoreAnalyzer(scores).getGrade()

            reviewContents = [row[1] for row in res]
            textSimGrade = TextAnalyzer(reviewContents,
                                        self._productTypeId).getSimGrade()
            emotionGrade = EmotionAnalyzer(reviewContents).getGrade()

            return scoreSimGrade, textSimGrade, emotionGrade
        finally:
            session.close()


def dumpParsedGradesToFile(outDirpath):
    if not path.exists(outDirpath):
        mkdir(outDirpath)

    session = Session()
    try:
        res = session.query(ProductType.id).all()
    finally:
        session.close()
        productTypeIds = [row[0] for row in res]
    for productTypeId in productTypeIds:
        filepath = path.join(outDirpath, '{}.txt'.format(productTypeId))
        with open(filepath, 'w') as fout:
            for (scoreGrade, textGrade,
                 emotionGrade) in ReviewUserAnalyzer(productTypeId):
                fout.write('{} {} {}\n'.format(scoreGrade, textGrade,
                                               emotionGrade))


if __name__ == '__main__':
    from sys import argv, stderr
    if len(argv) != 2:
        print('usage generateDataToParse.py outDirpath', file=stderr)
        exit(1)
    dumpParsedGradesToFile(argv[1])
