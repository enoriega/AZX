'''
Adapted from https://python.langchain.com/docs/expression_language/how_to/routing
'''

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=os.environ.get("OPENAI_API_KEY"),
    openai_organization=os.environ.get("OPENAI_ORGANIZATION")
)

# Create a chain which will classify questions
chain = (
    PromptTemplate.from_template(
        """Given the user question below, classify it as either being about `Health`, `Weather`, `Disease`, or `Other`.
            Do not respond with more than one word.

        <question>
        {question}
        </question>
        
        Classification:"""
    )
    | llm
    | StrOutputParser()
)

health_chain = (
    PromptTemplate.from_template(
        """You are an expert in health. \
Always answer questions starting with "As a health expert,". \
Respond to the following question:

Question: {question}
Answer:"""
    )
    | llm
)

disease_chain = (
    PromptTemplate.from_template(
        """You are an expert in disease. \
Always answer questions starting with "As a disease expert,". \
Respond to the following question:

Question: {question}
Answer:"""
    )
    | llm
)

weather_chain = (
    PromptTemplate.from_template(
        """You are an expert in weather. \
Always answer questions starting with "As a weather expert,". \
Respond to the following question:

Question: {question}
Answer:"""
    )
    | llm
)

general_chain = (
    PromptTemplate.from_template(
        """Respond to the following question:

Question: {question}
Answer:"""
    )
    | llm
)

queries = [
    "There is a storm coming. What should I do?",
    "I have a fever and am sneezing. What illnesses might I have?",
    "I have a fever and am sneezing. What should I do?",
    "What is a large language model?",
    "How should I prepare myself to be safe in a desert in the summer?"
]

query = queries[0]

def route(info):
    if "health" in info["topic"].lower():
        db_directory = "./data/health_db"
        specific_chain =  health_chain
    elif "disease" in info["topic"].lower():
        db_directory = "./data/disease_db"
        specific_chain = disease_chain
    elif "weather" in info["topic"].lower():
        db_directory = "./data/weather_db"
        specific_chain = weather_chain
    else:
        return general_chain.invoke({"question": query})

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory=db_directory, embedding_function=embedding_function)

    docs = db.similarity_search(query)
    combined_docs = "\n".join([doc.page_content for doc in docs])

    informed_query = info["question"] + \
                     "\nHere is additional information you may use:\n" + \
                     combined_docs

    return specific_chain.invoke({"question": informed_query})

full_chain = {"topic": chain, "question": lambda x: x["question"]} | RunnableLambda(
    route
)

print(full_chain.invoke({"question": query}).content)
