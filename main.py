from langchain.schema import StrOutputParser
from langchain.schema.runnable.config import RunnableConfig
import chainlit as cl
from langsmith import traceable
from langchain_core.runnables import RunnablePassthrough
from src.db import get_schema, run_query, extract_sql_from_text
from src.factory import LLMFactory, Stages, PromptFactory


@cl.step
async def generate_sql_query(question):
    sql_gen_model = LLMFactory.create(stage=Stages.GENERATE_SQL)
    sql_gen_prompt = PromptFactory.create_sql_prompt(schema=get_schema())
    sql_chain = (
            {"question": RunnablePassthrough()}
            | sql_gen_prompt
            | sql_gen_model
            | StrOutputParser()
    )
    return sql_chain.invoke(question)


@cl.step
async def execute_sql_query(sql_query):
    return run_query(sql_query)


@cl.step
async def generate_response(data, sql_query):
    answer_model = LLMFactory.create(stage=Stages.GENERATE_RESPONSE)
    synthesize_prompt = PromptFactory.create_synthetic_prompt(sql_query=sql_query, data=data)

    final_synthesize_chain = (
            {"question": RunnablePassthrough()}
            | synthesize_prompt
            | answer_model
            | StrOutputParser()
    )
    return final_synthesize_chain


@cl.on_message
@traceable
async def postgresql_chat_example(message: cl.Message):
    # Step 1: User Asks a Question
    question = message.content

    # Step 2: Generate SQL Query
    sql_query = await generate_sql_query(question)

    # Step 3: Execute SQL Query
    data = await execute_sql_query(sql_query)

    # Step 4: Return Answer to User
    synthesize_chain = await generate_response(data=data, sql_query=sql_query)

    msg = cl.Message(content="")
    output_msg = ""
    # Stream the response to the user (Step 4)
    async for chunk in synthesize_chain.astream(
        {"question": question},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)
        output_msg += chunk

    await msg.send()
    return output_msg
