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
  
collection_name = "new 2"
collection_id = "2019f262-82cd-49b8-a260-35e7b6fea966" # These values are only good on my local laptop (no secrets leaking)
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJhMzUwOTk0LTg4YjUtNGIyMi04NDA4LTk1MjhlZjU3ZGIyZiJ9.R0Atkx8qy5eFUq_NMuyaaQaaGYHzL0zRK_5sshImGK0"
token = "sk-d2e6c4d14d4444f8bcc13fd4a8217f83" # These values are only good on my local laptop (no secrets leaking)
model = "test:latest" 

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
	df = result.to_pandas()
	df.to_csv(f"results_{idx}.csv")
#df.append(result.to_pandas())

#results_file = "results.csv"
#if not os.path.exists(results_file):
#    with open(results_file, 'w') as file:
#        file.write("")

#df.to_csv(f"results.csv")

