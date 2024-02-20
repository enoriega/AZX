import pandas as pd
import chromadb
import fire
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_args(input_dir: str, output_dir: str) -> tuple:
    return input_dir, output_dir

def get_dfs(dir: str) -> list:
    return list(
        pd.read_excel(
            dir,
            sheet_name=[
                "Diseases, symptoms, treatments", 
                "Health hazards",
                "Adverse weather events"
            ]
        ).values()
    )

def get_dicts(df: pd.DataFrame) -> list:
    dicts = []

    for i in df.index:
        dictionary = {}
        
        for col in df.loc[i].index:
            dictionary[col] = df.loc[i, col]
        dicts.append(dictionary)
    return dicts
    
def get_text(dictionary: dict) -> str:
    if "Diseases" in dictionary:
        return dictionary["Diseases"] + "\n" + dictionary["Text content"]

    elif "Alert type" in dictionary:
        return dictionary["Alert type"] + "\n" + dictionary["Text content"]

    else:
        text = dictionary["Disease/health event"]
    
        if isinstance(dictionary["Symptoms"], str):
            text += "\n" + dictionary["Symptoms"]
        
        if isinstance(dictionary["Treatment(s)"], str):
            text += "\n" + dictionary["Treatment(s)"]

        return text

def get_metadatas(dictionary: dict) -> dict:
    metadatas = dictionary.copy()
    
    if "Diseases" in dictionary:
        metadatas.pop("Diseases")
        metadatas.pop("Text content")
        metadatas["Published"] = str(metadatas["Published"])
        metadatas["Sheet"] = "health"

    elif "Alert type" in dictionary:
        metadatas.pop("Alert type")
        metadatas.pop("Text content")
        metadatas["Published"] = str(metadatas["Published"])
        metadatas["Sheet"] = "weather"

    else:
        metadatas.pop("Disease/health event")
        metadatas.pop("Symptoms")
        metadatas.pop("Treatment(s)")
        metadatas["Sheet"] = "disease"

    return metadatas

def process_df(
    df: pd.DataFrame,
    text_splitter: RecursiveCharacterTextSplitter,
    collection: chromadb.api.models.Collection.Collection
) -> None:
    dicts = get_dicts(df)

    for i, dictionary in enumerate(dicts):
        text = get_text(dictionary)
        metadatas = get_metadatas(dictionary)

        documents = text_splitter.create_documents([text])
        contents = [doc.page_content for doc in documents]
        for j, content in enumerate(contents):
            collection.add(
                documents=content, 
                metadatas=metadatas,
                ids=["id" + str(i) + "-" + str(j)]
            )

def main():
    input_dir, output_dir = fire.Fire(get_args)
    dfs = get_dfs(input_dir)

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=400,
        chunk_overlap=30,
        length_function=len,
        is_separator_regex=False,
    )
    chroma_client = chromadb.PersistentClient(path=output_dir)
    collection = chroma_client.create_collection(name="langchain")

    for df in dfs:
        process_df(df, text_splitter, collection)

if __name__ == "__main__":
    main()