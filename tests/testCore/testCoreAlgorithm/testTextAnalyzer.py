import unittest
from os import getcwd
from sqlalchemy import func
from fakeReviewFilterWeb.core.coreAlgorithm.textAnalyzer \
    import TextAnalyzer, TextAnalysisMaxSSaver
from fakeReviewFilterWeb.core.infoDatabase.dbSession \
    import dbSession as Session
from fakeReviewFilterWeb.core.infoDatabase.reviewModels \
    import Review


class TestTextAnalyzer(unittest.TestCase):
    def testTextAnalysisMaxSSaver(self):
        print('current dir :{}'.format(getcwd()))
        maxSSaver = TextAnalysisMaxSSaver()
        print(maxSSaver._data)

    def testTextAnalyzer(self):
        session = Session()
        try:
            res = (session.query(Review.reviewUserId, Review.productTypeId).
                   group_by(Review.reviewUserId, Review.productTypeId).
                   having(func.count(Review.id) > 1).limit(1).one())
            userId, productTypeId = res
            res = (session.query(Review.reviewContent).
                   filter(Review.reviewUserId == userId and
                          Review.productTypeId == productTypeId).all())
            contents = [row[0] for row in res]
            print(contents)
            textAnalyzer = TextAnalyzer(contents, productTypeId)
            print(textAnalyzer.getSimGrade())
        finally:
            session.close()
