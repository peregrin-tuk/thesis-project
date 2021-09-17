import inspect
from src.generation.abstract_generator import AbstractGenerator
import src.generation.generators as generators_module


def get_available_generators():
    available_generators = []
    for _, obj in inspect.getmembers(generators_module):
        if inspect.isclass(obj) and issubclass(obj, AbstractGenerator) and obj is not AbstractGenerator:
            available_generators.append(obj)
    return available_generators