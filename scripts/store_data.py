import pandas as pd
import chromadb
import fire
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pandas import DataFrame
from tqdm import tqdm

def get_args(input_dir: str, output_dir: str) -> tuple:
    return input_dir, output_dir


def get_dfs(dir: str) -> dict[str, DataFrame]:
    return pd.read_excel(
                dir,
                sheet_name=[
                    "Diseases, symptoms, treatments",
                    "Health hazards",
                    "Adverse weather events",
                    "Shelters"
                ]
            )



def get_dicts(df: pd.DataFrame) -> list:
    dicts = []

    for i in df.index:
        dictionary = {}

        for col in df.loc[i].index:
            dictionary[col] = df.loc[i, col]
        dicts.append(dictionary)
    return dicts


def get_text(name: str, dictionary: dict) -> str:
    if name == "Adverse weather events":
        return f'Alert type: {dictionary["Alert type"]}\nSuggestion: {dictionary["Text content"]}'
    elif name == "Diseases, symptoms, treatments":
        return f'Disease: {dictionary["Disease/health event"]}\nSymptoms: {dictionary["Symptoms"]}\nTreatment: {dictionary["Treatment(s)"]}'
    elif name == "Shelters":
        return f'Name: {dictionary["Name"]}\nCommunity: {dictionary["Community"]}\nType: {dictionary["Type"]}\nAddress: {dictionary["Street Address"]}, {dictionary["County"]}, {dictionary["State"]}'
    elif name == "Health hazards":
        return f'Health hazard: {dictionary["Diseases"]}\nContext: {dictionary["Text content"]}'
    else:
        return ""


def get_metadatas(name: str, dictionary: dict) -> dict:
    if name == "Adverse weather events":
        md = {k:dictionary[k] for k in ["Source name", "URL", "Region", "Language"]}
        md['type'] = "weather"
    elif name == "Diseases, symptoms, treatments":
        md = {'URL': dictionary['Source'], 'type': "disease"}
    elif name == "Shelters":
        md = {'URL': dictionary['URL'], 'type': "shelter"}
    elif name == "Health hazards":
        md = {'Region': dictionary['Region'], 'type': "hazards"}
    else:
        md = dict()

    return md


def process_df(
        name: str,
        df: pd.DataFrame,
        text_splitter: RecursiveCharacterTextSplitter,
        collection: chromadb.api.models.Collection.Collection
) -> None:
    dicts = get_dicts(df)

    for i, dictionary in enumerate(tqdm(dicts, desc=f"Vectorizing {name}")):
        text = get_text(name, dictionary)
        if text:
            metadatas = get_metadatas(name, dictionary)

            documents = text_splitter.create_documents([text])
            contents = [doc.page_content for doc in documents]
            for j, content in enumerate(contents):
                collection.add(
                    documents=content,
                    metadatas=metadatas,
                    ids=[name + "-" + str(i) + "-" + str(j)]
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

    for name, df in dfs.items():
        process_df(name, df, text_splitter, collection)


if __name__ == "__main__":
    main()