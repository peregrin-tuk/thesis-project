
from pretty_midi.pretty_midi import PrettyMIDI
from src.evaluation.mgeval import analyze_pretty_midi, calc_distances


class Evaluation():

    def __init__(self, normalization_factors: dict = None):
        self.normalization_factors = normalization_factors


    def evaluate_similarity(self, result: PrettyMIDI, control: PrettyMIDI, features: list = None):
        if features is None:
            result_evaluation = analyze_pretty_midi(result)
            control_evaluation = analyze_pretty_midi(control)
            similarity_distances = calc_distances(result_evaluation, control_evaluation)
            return { 'absolute': similarity_distances, 'normalized': self.__normalize(similarity_distances)}
        else:
            selection = {}
            result_evaluation = analyze_pretty_midi(result)
            control_evaluation = analyze_pretty_midi(control)
            similarity_distances = calc_distances(result_evaluation, control_evaluation)
            for key in features:
                if key in similarity_distances:
                    result[key] = similarity_distances[key]
            return { 'absolute': selection, 'normalized': self.__normalize(selection)}
            


    def set_normalization_factors(self, normalization_factors: dict):
        self.normalization_factors = normalization_factors


    def __normalize(self, evaluation_results: dict):
        if self.normalization_factors is None:
            print('[EVAL] Error: No Normalization Factors set.')
        else:
            normalized_values = {}
            for key, value in evaluation_results.items():
                n = self.normalization_factors[key]
                normalized_values[key] = value / n
            return normalized_values
