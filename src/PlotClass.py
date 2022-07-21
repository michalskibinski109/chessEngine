import json
import matplotlib.pyplot as plt
import os

class PathNotExistException(Exception):
    pass

class Plot:
    def __init__(self, path='game.json', ev=[], times=[]):
        self.path = path
        self.evals = ev
        self.time_per_move = times
        self.max_eval = 5

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if os.path.exists(path):
            self.__path = path
        else:
            raise PathNotExistException

    def load_from_file(self):
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        self.evals = list(zip(*data['EVALUATIONS']))
        self.time_per_move = data['TIMES']
        if len(self.evals) != len(self.time_per_move):
            print(
                f'invalid data shapes: {len(self.evals)}, {len(self.time_per_move)}')

    def __call__(self):
        if len(self.evals) < 1:
            self.load_from_file()
        y = [round(e, 2) if abs(e) < self.max_eval else e *
             self.max_eval//abs(e) for e in self.evals[-1]]
        x = list(range(1, 1+len(y)))
        fig, axs = plt.subplots(2)
        fig.suptitle('eval and time per move')
        axs[0].bar(x, y)
        axs[0].set_ylabel('evaluation')
        axs[1].bar(list(range(1, 1+len(self.time_per_move))),
                   self.time_per_move)
        axs[1].set_xlabel('move')
        axs[1].set_ylabel('time [sec]')
        plt.show()
