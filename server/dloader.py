from langchain_community.llms import Ollama
MODEL="llama2"
model = Ollama (model=MODEL)
print('1',model.invoke("Tell me a joke"))

from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()

from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("mlschool.pdf")
pages = loader.load_and_split()
#print(pages)

from langchain.prompts import ChatPromptTemplate

template = """
Answer the question based on the context below. If you can't 
answer the question, reply "I don't know".

Context: {context}

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
prompt.format(context="Mary's younger sister is Susana", question="Who is Mary's sister?")

chain = prompt | model | parser

print(chain.invoke({
    "context": "Mary's younger sister is Susana",
    "question": "Who is Susana's  elder sister?"
}))