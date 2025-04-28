from langchain_community.llms import Ollama
MODEL="llama2"
model = Ollama (model=MODEL)
print('1',model.invoke("Tell me a joke"))

from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()
chain= model | parser
print('2',chain.invoke("Tell me a joke"))