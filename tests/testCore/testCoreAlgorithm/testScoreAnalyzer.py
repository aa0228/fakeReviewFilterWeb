import unittest
from fakeReviewFilterWeb.core.coreAlgorithm.scoreAnalyzer import ScoreAnalyzer


class TestScoreAnalyzer(unittest.TestCase):
    def testGrade(self):
        grade = ScoreAnalyzer([1, 1, 1, 1, 1]).getGrade()
        self.assertEqual(grade, 1)

        grade = ScoreAnalyzer([]).getGrade()
        self.assertEqual(grade, 0)
