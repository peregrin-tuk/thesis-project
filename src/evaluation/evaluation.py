from typing import List
from pretty_midi.pretty_midi import PrettyMIDI
from src.evaluation.mgeval import analyze_pretty_midi, calc_distances, calc_intra_set_distances


class Evaluation():

    def __init__(self, normalization_factors: dict = None):
        self.normalization_factors = normalization_factors


    def evaluate_similarity(self, result: PrettyMIDI, control: PrettyMIDI, features: list = None):
        result_evaluation = analyze_pretty_midi(result)
        control_evaluation = analyze_pretty_midi(control)
        similarity_distances = calc_distances(result_evaluation, control_evaluation)

        if features is None:
            return { 'absolute': similarity_distances, 'normalized': self.__normalize(similarity_distances)}
        else:
            selection = {}
            for key in features:
                if key in similarity_distances:
                    selection[key] = similarity_distances[key]
            return { 'absolute': selection, 'normalized': self.__normalize(selection)}


    def evaluate_variance(self, sequences: List[PrettyMIDI]):
        evals = []

        for s in sequences:
            evals.append(analyze_pretty_midi(s))

        return calc_intra_set_distances(evals)


    def set_normalization_factors(self, normalization_factors: dict):
        self.normalization_factors = normalization_factors


    # CHECK -> evtl. mit variance auch kompatibel machen, indem result_keys dynamisch ausm ersten element in der Liste ermittelt werden
    # TODO evtl. noch Error Handling für unerlaubten Input (list elemente nicht alle gleich oder keine dictionaries)
    def calc_avg_from_similarity_dicts(self, lst: List[dict]):
        """ 
        Takes a list of dictionaries as returned by evaluate_similarity(), calculates the average for each feature (both absolute and normalized) and returns a new dcit with the average values.

        Returns:
            dict: in the form of {'absolute': avg. absolute eval values, 'normalized': avg. noramlized eval values}

        """
        result = {'absolute': {}, 'normalized': {}}

        for result_key in result:
            for feature_key in lst[0][result_key]:
                total = 0
                for dictionary in lst:
                    total += dictionary[result_key][feature_key]
                avg = total / float(len(lst))
                result[result_key][feature_key] = avg
        
        return result


    def __normalize(self, evaluation_results: dict):
        if self.normalization_factors is None:
            print('[EVAL] Error: No Normalization Factors set.')
        else:
            normalized_values = {}
            for key, value in evaluation_results.items():
                n = self.normalization_factors[key]
                normalized_values[key] = value / n
            return normalized_values
