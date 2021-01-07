import search_engine_best
import search_engine_2
import search_engine_1
import gensim
from gensim.models import Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
if __name__ == '__main__':
    class callback(CallbackAny2Vec):
        """
        Callback to print loss after each epoch
        """

        def __init__(self):
            self.epoch = 0

        def on_epoch_end(self, model):
            loss = model.get_latest_training_loss()

            if self.epoch == 0:
                print('Loss after epoch {}: {}'.format(self.epoch, loss))
            elif self.epoch % 100 == 0:
                print('Loss after epoch {}: {}'.format(self.epoch, loss - self.loss_previous_step))
            self.epoch += 1
            self.loss_previous_step = loss
    #search_engine_best.main()
    search_engine_1.main()