import abc

from messangers.abstract_messanger import AbstractMessanger


class AbstractBridge(abc.ABC):

    def __init__(self, left: AbstractMessanger, right: AbstractMessanger) -> None:
        self.left = left
        self.right = right

    @abc.abstractmethod
    def run(self) -> None:
        pass
