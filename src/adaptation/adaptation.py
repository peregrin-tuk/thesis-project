from src.adaptation.adaptation_pipeline import AdaptationPipeline
from src.adaptation.operations.same_key_operation import SameKeyOperation

# this is more of a draft

# prepare a pipeline
pipeline = AdaptationPipeline()
pipeline.register(SameKeyOperation)


# # adapt a melody with the pipeline
# input_analysis = analyse(input_sequence, pipeline.required_analysis)
# pipeline.execute(gen_base_sequence, input_sequence, input_analysis)



