from ipywidgets import Output
from pprint import pprint

from src.db import generations as db
from src.db.reference_sets import fetch_ref_set_by_id, get_normalization_values_of_ref_set
from src.evaluation.evaluation import Evaluation


class AppExplore:


    def __init__(self, log: Output):
        self.log = log
        self.cr_sets = []
        self.generation_ids = []
        self.set_similarity_reference(5) # set default normalization values

    def run(self, idx: int):
        self.__clear_log()

        cr_set = db.read_generation_result_to_cr_set(idx)
        self.cr_sets.append(cr_set)
        self.generation_ids.append(idx)

        with self.log:
            pprint(cr_set)

        # NOTE this is not clean - Workaround to work with existing batch interface
        self.result = {
            'generations': self.cr_sets,
            'generation_avg_similarity': None,
            'adaptation_avg_similarity': None,
            'generation_variance': None,
            'adaptation_variance': None,
            'db_set_id': 'not available',
            'db_generation_ids': self.generation_ids,
        }

        return self.result


    def set_similarity_reference(self, ref_set_id: int):
        normalization_values = get_normalization_values_of_ref_set(ref_set_id)
        self.evaluation = Evaluation(normalization_values)

        ref_set = fetch_ref_set_by_id(ref_set_id)
        self.ref_set = ref_set['name'] + ' (' + ref_set['source'] + ')'


    def __log(self, msg: str):
        with self.log:
            print(msg)

    def __clear_log(self):
        self.log.clear_output()
        
