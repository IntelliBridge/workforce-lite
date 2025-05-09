from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from ragas import EvaluationDataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, LLMContextPrecisionWithReference, NoiseSensitivity, ResponseRelevancy
from ragas.run_config import RunConfig

import requests
import json
import os
from test_data.test_data import questions, ground_truths
from ChatCompletionsClient import ChatCompletionsClient
import pdb
  
collection_name = "new 4"
collection_id = "6e69d3f9-c7e7-433f-b63f-087bf0a136ad" # These values are only good on my local laptop (no secrets leaking)
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJhMzUwOTk0LTg4YjUtNGIyMi04NDA4LTk1MjhlZjU3ZGIyZiJ9.R0Atkx8qy5eFUq_NMuyaaQaaGYHzL0zRK_5sshImGK0"
token = "sk-5a487943ed3e4f548cb3ad4c2d7e6751" # These values are only good on my local laptop (no secrets leaking)
model = "gemma3:12b" 

client = ChatCompletionsClient(token)
# Inference
dataset = []
answers = []
contexts = []

for query, truth in zip(questions, ground_truths):

    references, answer = client.chat_with_collection(model,
                                    query,
                                    collection_id,
                                    collection_name)
    
    # To dict
    dataset.append(
            {
                "user_input":query,
                "retrieved_contexts": [x['document'][0] for x in references['sources']],
                "response": answer,
                "reference": truth
            }
        )
    
df = []
for idx, single_dataset in enumerate(dataset):
	single_dataset_list = [single_dataset]
	evaluation_dataset = EvaluationDataset.from_list(single_dataset_list)

	ollama_model = OllamaLLM(model=model)

	evaluator_llm = LangchainLLMWrapper(ollama_model)

	result = evaluate(dataset=evaluation_dataset, 
                  metrics=[
                           #LLMContextRecall(), 
                           #LLMContextPrecisionWithReference(), 
                           #Faithfulness(), 
                           FactualCorrectness() 
                           #NoiseSensitivity()
                           ],
                  llm=evaluator_llm,
                  run_config=RunConfig(timeout=3600,))
	df.append(result.to_pandas())

results_file = "results.csv"
if not os.path.exists(results_file):
    with open(results_file, 'w') as file:
        file.write("")

df.to_csv(f"results.csv")

