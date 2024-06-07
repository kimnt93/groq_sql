
SYNTHETIC_TEMPLATE = """**Task**: Create a response using the available Details while adhering to the following Rules:

**Rules**:
- Always ensure a response to the input question. If the query results lack relevant information, reply with "No relevant information found."
- Formulate your answer solely based on the information retrieved from the query results.
- Avoid prefaces such as "based on information", "according to the provided data", etc.

**Details**:
- Question: {question}
- SQL Query: {sql_query}
- Data: {data}
- Today: {today}

**Response**:"""


SQL_GEN_TEMPLATE = """**Task**: Convert human questions into PostgreSQL queries based on the provided Details. Adhere to the specific Rules.

**Rules**:
- Always limit the response results under 50 records.
- Convert the question into a query without any pre-amble.
- Do not use SELECT * statement, always list all columns explicitly.
- Provide details if you are joining tables.

**Details**:
- Schema: {schema}
- Human Question: {question}
- Today: {today}

**PostgreSQL**:"""
