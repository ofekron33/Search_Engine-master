class ConfigClass:
    def __init__(self):
        self.corpusPath = 'D:\\Downloads\\Data\\Data'
        self.savedFileMainFolder = '\\Postings'
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath
