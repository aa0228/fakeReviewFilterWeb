from sys import argv
from fakeReviewFilterWeb.core.infoDatabase.loadFileToDatabase import \
    loadFileToDatabase


if __name__ == '__main__':
    loadFileToDatabase(argv[1:])
    print('done!')
