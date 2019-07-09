import heapq
from os import path, mkdir
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
from .infoDatabase.dbSession import dbSession as Session
from .infoDatabase.reviewModels import Review
from .coreAlgorithm.scoreAnalyzer import ScoreAnalyzer
from .coreAlgorithm.textAnalyzer import TextAnalyzer
from .coreAlgorithm.emotionAnalyzer import EmotionAnalyzer


MODEL_SAVE_DIR_PATH = './randomForestModels'


class RandomForestModel:
    def __init__(self, productTypeId):
        self._productTypeId = productTypeId
        self._load()

    def _load(self):
        filepath = path.join(MODEL_SAVE_DIR_PATH, str(self._productTypeId))
        if path.exists(filepath):
            self._model = joblib.load(filepath)
        else:
            self._trainModel()
            self._save()

    def _getTrainData(self):
        """

        从数据库中录入训练数据

        """
        session = Session()
        try:
            res = session.query(Review.reviewUserId).\
                  filter(Review.productTypeId == self._productTypeId).all()
            userIds = [row[0] for row in res]

            trainData = []
            for userId in userIds:
                res = session.query(Review.reviewScore, Review.reviewContent).\
                      filter(Review.reviewUserId == userId and
                             Review.productTypeId == self._productTypeId).all()
                scores = [row[0] for row in res]
                scoreSimGrade = ScoreAnalyzer(scores).getGrade()

                reviewContents = [row[1] for row in res]
                textSimGrade = TextAnalyzer(reviewContents,
                                            self._productTypeId).getSimGrade()

                emotionGrade = EmotionAnalyzer(reviewContents).getGrade()

                trainData.append((scoreSimGrade, textSimGrade, emotionGrade))
            return trainData
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _getKthValue(self, iterator, k):
        """

        获得第k大的值

        """
        topK = [float('-inf') for i in range(k)]
        for value in iterator:
            if value > topK[0]:
                heapq.heappop(topK)
                heapq.heappush(topK, value)
        return topK[-1]

    def _getTarget(self, trainData):
        topRatio = 0.15
        kValue = int(len(trainData) * topRatio)
        scoreThreshold = self._getKthValue((record[0]
                                            for record in trainData), kValue)
        textThreshold = self._getKthValue((record[1]
                                           for record in trainData), kValue)
        emotionThreshold = self._getKthValue((record[2]
                                              for record in trainData), kValue)

        def fun(x, y, z):
            return ((x > scoreThreshold + y > textThreshold +
                     z > emotionThreshold) >= 2)
        return [int(fun(x, y, z)) for x, y, z in trainData]

    def _trainModel(self):
        trainData = self._getTrainData()
        target = self._getTarget(trainData)
        clf = RandomForestClassifier()
        clf.fit(trainData, target)
        self._model = clf

    def _save(self):
        if not path.exists(MODEL_SAVE_DIR_PATH):
            mkdir(MODEL_SAVE_DIR_PATH)
        joblib.dump(self._model,
                    path.join(MODEL_SAVE_DIR_PATH, str(self._productTypeId)))

    def predict(self, data):
        """

        data: a matrix
        return a list

        """
        return self._model.predict(data)

    def predictOne(self, data):
        """

        data: a list
        return a value

        1 is fake
        0 is real

        """
        return self._model.predict([data])[0]
