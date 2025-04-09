import json
from uuid import uuid4


def disk_writer(doc, folder):
    """
    Writes entire document to specified folder
    Param:
        doc: Document and associated metadata
        folder: Target folder to write to
    """
    file_name = doc[1]["source"]

    # Parse list to get page content and metadata
    data_dict = {"page_content": doc[0], "metadata": doc[1]}

    # Convert dictionary to json string
    json_data = json.dumps(data_dict)

    with open(f"{folder}{file_name}.json", "w") as file:
        file.write(json_data)


def disk_loader(docs, file_path):
    """
    Loads entire document and metadata
    from specified file_path
    and appends to list
    Param:
        docs: List to append document and metadata to
        file_path: Target file to read from
    """
    with open(file_path, "r") as file:
        json_data = json.load(file)
        docs.append([json_data["page_content"], json_data["metadata"]])


def chunk_disk_writer(doc, folder, idx):
    """
    Writes chunk of document to specified folder
    Param:
        doc: chunk and associated metadata
        folder: Target folder to write to
        idx: Unique id
    """
    # Clean metadata with only container name and file name
    index = doc[2].rfind(f"/")
    file_name = doc[2][index:]

    index = file_name.rfind(".")
    file_name = file_name[:index] + f"_chunk_{idx}"

    data_dict = {"text": doc[0], "vector_field": doc[1], "metadata": doc[2]}
    json_data = json.dumps(data_dict)

    with open(f"{folder}{file_name}.json", "w") as file:
        file.write(json_data)


def chunk_disk_loader(docs, file_path):
    """
    Loads chunk of document and metadata
    from specified file_path
    and appends to list
    Param:
        docs: List to append chunk and metadata to
        file_path: Target file to read from
    """
    with open(file_path, "r") as file:
        json_data = json.load(file)
        docs.append(json_data)


def bulk_disk_writer(doc, folder):
    """
    Writes bulk-prepared chunk document to specified folder
    Param:
        doc: Document and associated metadata
        folder: Target folder to write to
    """
    # Clean metadata with only container name and file name
    index = doc[1]["metadata"].rfind("/")
    file_name = doc[1]["metadata"][index:]
    index = file_name.rfind(".")
    file_name = file_name[:index] + "_bulk" + f"_chunk_{uuid4()}"

    json_data = json.dumps(doc)

    with open(f"{folder}/{file_name}.json", "w") as file:
        file.write(json_data)


def bulk_disk_loader(docs, file_path):
    """
    Loads bulk-prepared chunk document and metadata
    from specified file_path
    and appends to list
    Param:
        docs: List to append chunk and metadata to
        file_path: Target file to read from
    """
    with open(file_path, "r") as file:
        json_data = json.load(file)
        docs.append(json_data[0])
        docs.append(json_data[1])
