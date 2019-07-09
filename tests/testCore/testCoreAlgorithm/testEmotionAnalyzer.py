import unittest
from fakeReviewFilterWeb.core.coreAlgorithm.emotionAnalyzer \
    import EmotionAnalyzer


class TestEmotionAnalyzer(unittest.TestCase):
    def test(self):
        contents = ['hello world', 'nice to meet you!', 'good', 'hey']
        emotionAnalyzer = EmotionAnalyzer(contents)
        print(emotionAnalyzer.getGrade())
