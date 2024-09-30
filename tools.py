import datetime

import pandas as pd
import numpy as np

from db import VectorDB

data  = pd.read_csv("data/file_info_1.csv")
vb = VectorDB(data)
vb.create_db()

def search_for_links(query):

    try:
        results = vb.send_query(query, constraint={"$and" : [{"source": 'web'}, {"file_type": "web link"}]})
        results = pd.DataFrame(results["metadatas"][0])
        results = results.tail(1)

        return results, {"link retrieved" : True, 'message': None}

    except Exception as e:
        return None, {"link retrieved" : False, 'message': str(e)}

def search_for_similar_records(query, file_source="any", file_extension="any", file_size="any", nfiles_to_return=10, start_date="2024-01-01", end_date="2024-09-29"):
    """
    Function to search for similar records based on query and constraints.

    Args:
    query (str): The search query.
    file_source (str, optional): The file source location. Default is "any".
    file_extension (str, optional): The file extension type. Default is "any".
    file_size (str, optional): The size of the file. Default is "any".
    start_date (str, optional): Start date for filtering results. Format 'YYYY-MM-DD'. Default is '2024-01-01'.
    end_date (str, optional): End date for filtering results. Format 'YYYY-MM-DD'. Default is '2024-09-29'.

    Returns:
    tuple: Contains a DataFrame with results, a dictionary of result information, and a dictionary indicating success or failure.
    """

    result_info = {
        "number_of_matches": 0,
        "query_passed": query,
        "document_summary": "No files found",
        "latest_document_created_at": "None"
        }

    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        const = []

        if file_source != "any":
            constraint = {"source": file_source}
            const.append(constraint)

        if file_extension != "any":
            constraint = {"file_type": file_extension}
            const.append(constraint)

        if file_size != "any":
            constraint = {"file_size": {"$lte": int(file_size)}}
            const.append(constraint)

        if len(const) > 0:

            if len(const) == 2:
                constraint = {"$and": const}
            else:
                constraint = const[0]

            results = vb.send_query(query, constraint)
        else:
            results = vb.send_query(query)

        results = pd.DataFrame(results["metadatas"][0])
        print("Meta data\n", results)

        if results.shape[0] > 0:
            results['file_created_at'] = pd.to_datetime(results['file_created_at']).dt.date
            results = results[(results['file_created_at'] >= start_date) & (results['file_created_at'] <= end_date)]

            if file_source != "any":
                results = results[results['source'] == file_source]

            if file_extension != "any":
                results = results[results['file_type'] == file_extension]

            if file_size != "any":
                results = results[results['file_size'] >= (file_size * 1000)]

            result_info = {
                "number_of_matches": results.shape[0],
                "query_passed": query,
                "document_summary": "/".join(results["file_title"].values),
                "latest_document_created_at": results["file_created_at"].max()
            }

            results = results.sort_values(by='file_created_at')
            results = results.tail(int(nfiles_to_return))

        return results, result_info, {"success": True}

    except Exception as e:
        return "Error faced while processing data",  result_info, {"success": False, "exception": str(e)}
