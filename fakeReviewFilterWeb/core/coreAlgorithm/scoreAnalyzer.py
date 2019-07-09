from math import isnan


class ScoreAnalyzer:
    def __init__(self, scores):
        self._scores = scores

    def _getScoreSimGrade(self):
        totalDiff = 0
        count = 0
        for front in range(len(self._scores) - 1):
            for back in range(front + 1, len(self._scores)):
                totalDiff += abs(self._scores[front] - self._scores[back])
                count += 1
        if not count:
            return 0
        m = 1 + totalDiff / count
        return 1 / m

    def getGrade(self):
        res = float(self._getScoreSimGrade())
        if isnan(res):
            return 0
        return res
