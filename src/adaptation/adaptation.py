from src.adaptation.adaptation_pipeline import AdaptationPipeline
from src.adaptation.operations.transpose_sequence_operation import TransposeSequenceOperation

# this is more of a draft

# prepare a pipeline
pipeline = AdaptationPipeline()
pipeline.register(TransposeSequenceOperation)


# # adapt a melody with the pipeline
# input_analysis = analyse(input_sequence, pipeline.required_analysis)
# pipeline.execute(gen_base_sequence, input_sequence, input_analysis)



