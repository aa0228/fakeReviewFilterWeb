import unittest
from fakeReviewFilterWeb.core.infoDatabase.loadFileToDatabase import\
    loadFileToDatabase


class TestLoadFileToDatabase(unittest.TestCase):
    @unittest.skip('已测试,仅测试数据库即可')
    def testLoadFileToDatabase(self):
        filepaths = ['/home/moon/programming/python/fakeReviewFilter/fakeReviewFilter/data/Jewelry.txt']
        loadFileToDatabase(filepaths)
