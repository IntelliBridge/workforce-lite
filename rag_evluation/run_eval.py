from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from ragas import EvaluationDataset
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, LLMContextPrecisionWithReference, NoiseSensitivity, ResponseRelevancy
from ragas.run_config import RunConfig

import requests
import json

from test_data.test_data import questions, ground_truths
from ChatCompletionsClient import ChatCompletionsClient
import pdb
  
collection_name = "Meeting Notes"
collection_id = "5d1a65f0-c501-4e24-b27b-f77520893115" # These values are only good on my local laptop (no secrets leaking)
# token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjJhMzUwOTk0LTg4YjUtNGIyMi04NDA4LTk1MjhlZjU3ZGIyZiJ9.R0Atkx8qy5eFUq_NMuyaaQaaGYHzL0zRK_5sshImGK0"
token = "sk-cc18c4d2da1d4d8f8f512e1e4796a109" # These values are only good on my local laptop (no secrets leaking)
model = "dylans-model:latest" 

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
    

evaluation_dataset = EvaluationDataset.from_list(dataset)

ollama_model = OllamaLLM(model="dylans-model:latest")

evaluator_llm = LangchainLLMWrapper(ollama_model)

result = evaluate(dataset=evaluation_dataset, 
                  metrics=[
                           LLMContextRecall(), 
                           LLMContextPrecisionWithReference(), 
                           Faithfulness(), 
                           FactualCorrectness(), 
                           NoiseSensitivity()
                           ],
                  llm=evaluator_llm,
                  run_config=RunConfig(timeout=3600,))


df = result.to_pandas()
df.to_csv("results")


