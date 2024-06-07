from functools import lru_cache
import re

from langchain_community.utilities import SQLDatabase

# Database URI for connecting to the PostgreSQL database
_DB_URI = "postgresql+psycopg2://nba_sql:nba_sql@localhost:5432/nba"
# Creating an SQLDatabase engine instance using the provided URI
_DB_ENGINE = SQLDatabase.from_uri(_DB_URI)


def extract_sql_from_text(text):
    """
    Extracts SQL code from a given text.

    Args:
        text (str): The input text containing potential SQL code.

    Returns:
        str: Extracted SQL code or an empty string if no valid SQL is found.
    """
    # Regex pattern to match code blocks enclosed in triple backticks with 'sql' language identifier
    code_block_pattern = re.compile(r'```sql\s*(.*?)\s*```', re.DOTALL)
    # Regex pattern to match standalone SQL statements
    sql_pattern = re.compile(r'(SELECT.*?;)', re.DOTALL | re.IGNORECASE)

    # Try to find a code block enclosed in triple backticks
    match = code_block_pattern.search(text)
    if match:
        # If a code block is found, extract the SQL code within it
        sql_code = match.group(1).strip()
    else:
        # If no code block is found, try to find a standalone SQL statement
        match = sql_pattern.search(text)
        if match:
            # If a standalone SQL statement is found, extract it
            sql_code = match.group(1).strip()
        else:
            # If no SQL code is found, return an empty string
            sql_code = ""

    return sql_code


@lru_cache(maxsize=255)
def get_schema():
    """
    Retrieves the database schema information and caches the result.

    Returns:
        str: A string containing table information of the database.
    """
    return _DB_ENGINE.get_table_info()


def run_query(sql_query):
    """
    Runs a SQL query against the database and returns the results.

    Args:
        sql_query (str): The SQL query to be executed.

    Returns:
        list: The results of the SQL query as a list of dictionaries, or an empty list in case of an error.
    """
    try:
        # Extract SQL code from the input query text
        sql_query = extract_sql_from_text(sql_query)
        # If no valid SQL code is found, return an empty list
        if sql_query is None or sql_query == "":
            return []
        # Run the SQL query and return the results
        return _DB_ENGINE.run(sql_query)
    except Exception as ex:
        # Print the exception if any error occurs and return an empty list
        print(ex)
        return []
