import pickle


class NoSuchDataError(Exception):
    def __init__(self, info):
        super(NoSuchDataError, self).__init__(info)


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance


class DataSaver(metaclass=Singleton):
    def __init__(self, saveFilepath):
        self._saveFilepath = saveFilepath
        self._data = None

    def _loadDataFromFile(self):
        with open(self._saveFilepath, 'rb') as fin:
            self._data = pickle.load(fin)

    def _saveDataToFile(self):
        with open(self._saveFilepath, 'wb') as fout:
            pickle.dump(self._data, fout)

    def __enter__(self):
        return self

    def __exit__(self, excType, excValue, traceback):
        self._saveDataToFile()

    def getData(self, key):
        if key not in self._data:
            raise NoSuchDataError('no such data saved :{}'.format(key))
        return self._data[key]

    def setData(self, key, value):
        self._data[key] = value
