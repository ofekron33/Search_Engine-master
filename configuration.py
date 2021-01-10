import os
class ConfigClass:
    def __init__(self):
        # link to a zip file in google drive with your pretrained model
        self._model_url = "https://drive.google.com/file/d/1GG7rOfs4S52ZWsjlc_LVgvGVRH9Chu8G/view?usp=sharing"
        self._model=None
        self._download_model = True
        self._model_dir = ''
        self.corpusPath = ''
        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "/WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "/WithoutStem"
        self.toStem = False
        self.google_news_vectors_negative300_path = '../../../../GoogleNews-vectors-negative300.bin'
        self.glove_twitter_27B_25d_path = '../../../../glove.twitter.27B.25d.txt'
    def get__corpusPath(self):
        return self.corpusPath

    def get_model_url(self):
        return self._model_url

    def get_download_model(self):
        return self._download_model
    def set_model(self,model):
        self._model=model
    @property
    def model_dir(self):
        return self._model_dir

    @model_dir.setter
    def model_dir(self, model_dir):
        self._model_dir = model_dir

    def get_model_file(self):
        s = ''
        flag=False
        while flag==False:
            for r, d, f in os.walk(os.getcwd()):
                for file in f:
                    if file.endswith("model0601test1a.bin"):
                        s = os.path.join(r, file)
                        flag=True
        return s