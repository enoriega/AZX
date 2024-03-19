import csv

from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser


def load_data(path: str):
    with open(path) as f:
        reader = csv.DictReader(f, delimiter='\t')
        ret = [Document(page_content=r['Text content']) for r in reader]

    return ret

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
    # rag_prompt = hub.pull("rlm/rag-prompt")
    rag_prompt = PromptTemplate.from_template(
        "You are a public health advocate. Use the following documents to answer the question. If "
        "you don't know the answer, just say that you don't know. Enumerate the actionable items as clear and concise. For each action item, if there is a relevant document that includes a URL, include the URL for reference. "
        "bullets in a list. Write a follow up sentence that briefly elaborates the main sentence in each."
        "item.\nQuestion: {question} \nContext: {context} \nAnswer:")
    retriever = vectorstore.as_retriever()

    rag_chain = ({
                     "context": retriever | RunnableLambda(parse_docs),
                     "question": RunnablePassthrough()
                 }

                 | rag_prompt | llm)

    return rag_chain


if __name__ == "__main__":
    llm = ChatOpenAI(temperature=0, model='gpt-4-1106-preview')
    # rag_chain = build_rag_chain("azx_data.tsv", llm)
    chain = build_rag_chain("/Users/enoriega/github/AZX/scripts/resources", llm)

    # x = rag_chain.invoke("What should I do in the presence of poor air quality?")

    from fastapi import FastAPI
    from langserve import add_routes
    import uvicorn

    app = FastAPI(
        title="LangChain Server",
        version="1.0",
        description="A simple api server using Langchain's Runnable interfaces",
    )

    add_routes(
        app,
        chain
    )

    uvicorn.run(app, host="localhost", port=8000)
