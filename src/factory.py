import os
from dataclasses import dataclass
import datetime
from functools import lru_cache

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from src.prompt import SQL_GEN_TEMPLATE, SYNTHETIC_TEMPLATE


@dataclass
class Stages:
    """
    Dataclass representing different stages in the process.
    """
    GENERATE_SQL = 0
    GENERATE_RESPONSE = 1


class PromptFactory:
    """
    Factory class for creating different types of prompt templates.
    """

    @staticmethod
    def create_synthetic_prompt(sql_query, data):
        """
        Creates a synthetic prompt using the given SQL query and data.

        Args:
            sql_query (str): The SQL query to be included in the prompt.
            data (any): The data to be included in the prompt.

        Returns:
            PromptTemplate: The created prompt template.
        """
        return PromptTemplate(
            template=SYNTHETIC_TEMPLATE,
            input_variables=["question"],
            partial_variables={
                "sql_query": sql_query,
                "data": data,
                "today": datetime.datetime.now()
            }
        )

    @staticmethod
    def create_sql_prompt(schema):
        """
        Creates an SQL generation prompt using the given schema.

        Args:
            schema (str): The schema to be included in the prompt.

        Returns:
            PromptTemplate: The created prompt template.
        """
        return PromptTemplate(
            template=SQL_GEN_TEMPLATE,
            input_variables=["question"],
            partial_variables={
                "schema": schema,
                "today": datetime.datetime.now()
            }
        )


class LLMFactory:
    """
    Factory class for creating language model instances for different stages.
    """

    @staticmethod
    @lru_cache(maxsize=255)
    def create(stage: Stages):
        """
        Creates a language model instance based on the given stage.

        Args:
            stage (Stages): The stage for which the language model is to be created.

        Returns:
            ChatGroq: The created language model instance.

        Raises:
            ValueError: If an invalid stage is provided.
        """
        if Stages.GENERATE_SQL == stage:
            # Create a language model instance for generating SQL
            return ChatGroq(
                groq_api_key=os.environ['GROQ_API_KEY'],
                model_name="llama3-70b-8192"
            )
        elif Stages.GENERATE_RESPONSE == stage:
            # Create a language model instance for generating responses
            return ChatGroq(
                groq_api_key=os.environ['GROQ_API_KEY'],
                model_name="llama3-8b-8192",
                streaming=True,
                temperature=0.7
            )
        else:
            # Raise an error for invalid stage
            raise ValueError("Invalid stage")
