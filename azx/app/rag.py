import csv
from typing import Optional, Any

from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableLambda, Runnable, RunnableConfig
from langchain_core.runnables.utils import Input, Output
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser


class RetrieverWrapper(Runnable):
    def __init__(self, retriever):
        self.retriever = retriever

    def invoke(self, input: Input, config: Optional[RunnableConfig] = None) -> Output:
        return self.retriever.invoke(input=input['query'], config=config)

    async def ainvoke(self, input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any) -> Output:
        return await self.retriever.ainvoke(input=input['query'], config=config, **kwargs)


def parse_docs(documents):
    ret = list()
    for d in documents:
        data = f"Document: ```{d.page_content}```"
        if 'URL' in d.metadata:
            data += f"\nURL: {d.metadata['URL']}"
        ret.append(data)

    return ret


def build_rag_chain(path: str, llm):
    # documents = load_data(path)
    #
    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # splits = text_splitter.split_documents(documents)
    # vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=path, embedding_function=embeddings)
    completedb = vectorstore.as_retriever(search_kwargs={"k": 10})
    weatherdb = vectorstore.as_retriever(search_kwargs={"k": 10, "filter": {"type": "weather"}})
    healthdb = vectorstore.as_retriever(search_kwargs={"k": 10})
    diseasedb = vectorstore.as_retriever(search_kwargs={"k": 10})
    shelterdb = vectorstore.as_retriever(search_kwargs={"k": 10, "filter": {"type": "shelter"}})

    def choose_retriever(info):
        topic = info['topic'].content.lower().strip()
        if topic == "weather":
            return RetrieverWrapper(weatherdb)
        elif topic == "health":
            return RetrieverWrapper(healthdb)
        elif topic == "disease":
            return RetrieverWrapper(diseasedb)
        elif topic == "shelter":
            return RetrieverWrapper(shelterdb)
        else:
            return RetrieverWrapper(completedb)

    topic_classifier = (PromptTemplate.from_template(
        """Given the user question below, classify it as either being about `Health`, `Weather`, `Disease`, `Shelter` or `Other`.
            Do not respond with more than one word.

            <question>
                {question}
            </question>

        Classification:""") | llm)

    rag_prompt = PromptTemplate.from_template(
        "You are a public health advocate. Use the following documents to answer the question. If "
        "you don't know the answer, just say that you don't know. Enumerate the actionable items as clear and concise. For each action item, if there is a relevant document that includes a URL, include the URL for reference. "
        "bullets in a list. Write a follow up sentence that briefly elaborates the main sentence in each."
        "item.\nQuestion: {question} \nContext: {context} \nAnswer:")

    rag_chain = ({
                     "context": {
                                    "topic": {"question": RunnablePassthrough()} | topic_classifier,
                                    "query": RunnablePassthrough()
                                } | RunnableLambda(choose_retriever) | RunnableLambda(parse_docs),
                     "question": RunnablePassthrough()
                 }

                 | rag_prompt | llm)

    return rag_chain


if __name__ == "__main__":
    llm = ChatOpenAI(temperature=0, model='gpt-4-1106-preview')
    # rag_chain = build_rag_chain("azx_data.tsv", llm)
    chain = build_rag_chain("/Users/enoriega/github/AZX/scripts/resources2", llm)

    # x = rag_chain.invoke("What should I do in the presence of poor air quality?")

    # x = chain.invoke("I feel fever, chills and headache. What could I have?")
    # print(x)

