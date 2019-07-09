from math import isnan
import numpy as np
from textblob import TextBlob


class EmotionAnalyzer(object):
    def __init__(self, comments):
        self._commentdAnalysied = {}
        for comment in comments:
            textBlob = TextBlob(comment)
            self._commentdAnalysied[comment] = (textBlob.polarity + 1) / 2

        self._removeMaxAndMin()
        self._initPolarities()

    def _removeMaxAndMin(self):
        """

        去掉最大值和最小值

        """
        minKey = None
        minValue = float('inf')

        maxKey = None
        maxValue = float('-inf')
        for key, value in self._commentdAnalysied.items():
            if value < minValue:
                minValue = value
                minKey = key

            if value > maxValue:
                maxValue = value
                maxKey = key

        if minKey in self._commentdAnalysied:
            self._commentdAnalysied.pop(minKey)
        if maxKey in self._commentdAnalysied:
            self._commentdAnalysied.pop(maxKey)

    def _initPolarities(self):
        self._polarities = np.array(list(self._commentdAnalysied.values()),
                                    dtype=np.float64)

    def _average(self):
        """

        评论中的情感平均值

        """
        return self._polarities.mean()

    def _variance(self):
        """

        评论中的情感相似度方差

        """
        return np.var(self._polarities)

    def getGrade(self):
        res = self._variance()
        if isnan(res):
            return 0
        return float(res)
