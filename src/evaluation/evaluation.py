from typing import List
from pretty_midi.pretty_midi import PrettyMIDI
from src.evaluation.mgeval import analyze_pretty_midi, calc_distances, calc_intra_set_distances


class Evaluation():

    pitch_related_keys = ['pitch_count', 'pitch_class_histogram', 'pitch_class_transition_matrix', 'avg_pitch_interval', 'pitch_range']
    rhythm_related_keys = ['note_count', 'note_length_histogram', 'note_length_transition_matrix', 'avg_ioi', 'ioi_histogram', 'ioi_transition_matrix']

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
        """ 
        Takes a list of dictionaries as returned by evaluate_similarity(), calculates the average distance between the values of each feature based on exhaustive cross validation.
        Note: Currently returns the average inter-set distance + the average inter-set distance normalized by the similarity ref set.
        This might be revised in the future to another statistical value.

        Returns:
            dict: in the form of {'absolute': avg. absolute eval values, 'normalized': avg. normalized eval values}

        """
        evals = []

        for s in sequences:
            evals.append(analyze_pretty_midi(s))

        distances = calc_intra_set_distances(evals)
        keys = evals[0].keys()
        result = {}

        for i, key in enumerate(keys):
            total = 0
            count = 0
            for el in distances:
                for distance in el[i]:
                    total += distance
                    count += 1

            result[key] = total / float(count)

        return { 'absolute': result, 'normalized': self.__normalize(result)}





    def set_normalization_factors(self, normalization_factors: dict):
        self.normalization_factors = normalization_factors



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

    def calc_meta_scores(self, evaluation_dict: dict):
        total = 0
        for key, value in evaluation_dict.items():
            total += float(value)
        avg = total / float(len(evaluation_dict))

        total = 0
        for key in self.pitch_related_keys:
            total += float(evaluation_dict[key])
        pitch_avg = total / float(len(self.pitch_related_keys))

        total = 0
        for key in self.rhythm_related_keys:
            total += float(evaluation_dict[key])
        rhythm_avg = total / float(len(self.rhythm_related_keys))


        return {
            'avg': avg,
            'pitch_related_avg': pitch_avg,
            'rhythm_related_avg': rhythm_avg
        }



    def __normalize(self, evaluation_results: dict):
        if self.normalization_factors is None:
            print('[EVAL] Error: No Normalization Factors set.')
        else:
            normalized_values = {}
            for key, value in evaluation_results.items():
                n = self.normalization_factors[key]
                normalized_values[key] = value / n
            return normalized_values
