from abc import ABC, abstractmethod 

class AbstractGenerator(ABC):

    base_path = '../../models'

    @abstractmethod
    def __init__(self):
        pass
    