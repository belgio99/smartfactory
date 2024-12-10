"""
Question answering over an RDF or OWL graph using SPARQL.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts.base import BasePromptTemplate
from pydantic import Field
import re

from langchain_community.chains.graph_qa.prompts import (
    SPARQL_GENERATION_SELECT_PROMPT,
    SPARQL_GENERATION_UPDATE_PROMPT,
    SPARQL_INTENT_PROMPT,
    SPARQL_QA_PROMPT,
)
from langchain_community.graphs.rdf_graph import RdfGraph

import warnings
warnings.filterwarnings("ignore")

def trim_query(query: str) -> str:
    """
    Trims a SPARQL query to remove unnecessary parts and returns only the essential query components.

    Args:
        query (str): The SPARQL query string to be trimmed.

    Returns:
        str: A trimmed SPARQL query string containing only the necessary components.
    """
    # Match everything before the WHERE clause and the WHERE clause content itself, considering nested braces
    pattern = r"^(.*?)(WHERE\s*{(?:[^{}]*|{[^{}]*})*})"
    match = re.search(pattern, query, re.DOTALL)  # re.DOTALL allows '.' to match newline characters
    
    if match:
        return match.group(1) + match.group(2)  # Return everything before WHERE and the WHERE clause content
    
    return query  # If no WHERE clause is found, return the original query

class GraphSparqlQAChain(Chain):
    """
    A chain for performing question-answering against an RDF or OWL graph by generating SPARQL statements.

    Security note: Ensure that database connection credentials are narrowly scoped to avoid dangerous operations.
    
    Args:
        graph (RdfGraph): The RDF graph instance.
        sparql_generation_select_chain (LLMChain): The chain for generating SELECT SPARQL queries.
        sparql_generation_update_chain (LLMChain): The chain for generating UPDATE SPARQL queries.
        sparql_intent_chain (LLMChain): The chain for determining the intent of a query.
        qa_chain (LLMChain): The chain for answering questions based on the query.
        return_sparql_query (bool, optional): Whether to return the generated SPARQL query. Defaults to False.
        input_key (str, optional): The key for input queries. Defaults to "query".
        output_key (str, optional): The key for output results. Defaults to "result".
        sparql_query_key (str, optional): The key for returning the SPARQL query. Defaults to "sparql_query".
        allow_dangerous_requests (bool, optional): Whether to allow dangerous requests. Defaults to False.

    Raises:
        ValueError: If allow_dangerous_requests is not set to True.
    """

    graph: RdfGraph = Field(exclude=True)
    sparql_generation_select_chain: LLMChain
    sparql_generation_update_chain: LLMChain
    sparql_intent_chain: LLMChain
    qa_chain: LLMChain
    return_sparql_query: bool = False
    input_key: str = "query"  #: :meta private:
    output_key: str = "result"  #: :meta private:
    sparql_query_key: str = "sparql_query"  #: :meta private:

    allow_dangerous_requests: bool = False
    """Forced user opt-in to acknowledge that the chain can make dangerous requests."""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the GraphSparqlQAChain.

        Args:
            **kwargs: Additional keyword arguments passed to the parent class and the chain initialization.

        Raises:
            ValueError: If `allow_dangerous_requests` is not set to True.
        """
        super().__init__(**kwargs)
        if self.allow_dangerous_requests is not True:
            raise ValueError(
                "In order to use this chain, you must acknowledge that it can make "
                "dangerous requests by setting `allow_dangerous_requests` to `True`."
                "You must narrowly scope the permissions of the database connection "
                "to only include necessary permissions. Failure to do so may result "
                "in data corruption or loss or reading sensitive data if such data is "
                "present in the database."
                "Only use this chain if you understand the risks and have taken the "
                "necessary precautions. "
                "See https://python.langchain.com/docs/security for more information."
            )

    @property
    def input_keys(self) -> List[str]:
        """
        Returns the input keys for the chain.

        Returns:
            List[str]: A list containing the input key.
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """
        Returns the output keys for the chain.

        Returns:
            List[str]: A list containing the output key.
        """
        _output_keys = [self.output_key]
        return _output_keys

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        *,
        qa_prompt: BasePromptTemplate = SPARQL_QA_PROMPT,
        sparql_select_prompt: BasePromptTemplate = SPARQL_GENERATION_SELECT_PROMPT,
        sparql_update_prompt: BasePromptTemplate = SPARQL_GENERATION_UPDATE_PROMPT,
        sparql_intent_prompt: BasePromptTemplate = SPARQL_INTENT_PROMPT,
        **kwargs: Any,
    ) -> GraphSparqlQAChain:
        """
        Initializes the GraphSparqlQAChain from an LLM.

        Args:
            llm (BaseLanguageModel): The language model to use for query generation and answering.
            qa_prompt (BasePromptTemplate, optional): The prompt template for question answering. Defaults to SPARQL_QA_PROMPT.
            sparql_select_prompt (BasePromptTemplate, optional): The prompt template for generating SELECT queries. Defaults to SPARQL_GENERATION_SELECT_PROMPT.
            sparql_update_prompt (BasePromptTemplate, optional): The prompt template for generating UPDATE queries. Defaults to SPARQL_GENERATION_UPDATE_PROMPT.
            sparql_intent_prompt (BasePromptTemplate, optional): The prompt template for identifying query intent. Defaults to SPARQL_INTENT_PROMPT.
            **kwargs: Additional keyword arguments passed to the chain initialization.

        Returns:
            GraphSparqlQAChain: An initialized instance of GraphSparqlQAChain.
        """
        qa_chain = LLMChain(llm=llm, prompt=qa_prompt)
        sparql_generation_select_chain = LLMChain(llm=llm, prompt=sparql_select_prompt)
        sparql_generation_update_chain = LLMChain(llm=llm, prompt=sparql_update_prompt)
        sparql_intent_chain = LLMChain(llm=llm, prompt=sparql_intent_prompt)

        return cls(
            qa_chain=qa_chain,
            sparql_generation_select_chain=sparql_generation_select_chain,
            sparql_generation_update_chain=sparql_generation_update_chain,
            sparql_intent_chain=sparql_intent_chain,
            **kwargs,
        )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        """
        Processes the input query and generates a SPARQL query, which is used to retrieve an answer from the RDF graph.

        Args:
            inputs (Dict[str, Any]): A dictionary containing the input query.
            run_manager (Optional[CallbackManagerForChainRun], optional): The callback manager for chain execution. Defaults to None.

        Returns:
            Dict[str, str]: A dictionary containing the result of the query or an error message.
        """
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        prompt = inputs[self.input_key]

        # Set intent to "SELECT" for now
        intent = 'SELECT'
        sparql_generation_chain = self.sparql_generation_select_chain

        _run_manager.on_text("Identified intent:", end="\n", verbose=self.verbose)
        _run_manager.on_text(intent, color="green", end="\n", verbose=self.verbose)

        generated_sparql = sparql_generation_chain.run(
            {"prompt": prompt, "schema": self.graph.get_schema}, callbacks=callbacks
        )

        generated_sparql = generated_sparql.replace("`", "").replace("sparql", "").strip()
        generated_sparql = "\n".join(generated_sparql.split("\n")[0:])
        generated_sparql = trim_query(generated_sparql)

        _run_manager.on_text("Generated SPARQL:", end="\n", verbose=self.verbose)
        _run_manager.on_text(
            generated_sparql, color="green", end="\n", verbose=self.verbose
        )

        if intent == "SELECT":
            context = self.graph.query(generated_sparql)

            _run_manager.on_text("Full Context:", end="\n", verbose=self.verbose)
            _run_manager.on_text(
                str(context), color="green", end="\n", verbose=self.verbose
            )
            result = self.qa_chain(
                {"prompt": prompt, "context": context, "query": generated_sparql},
                callbacks=callbacks,
            )
            res = result[self.qa_chain.output_key]
        elif intent == "UPDATE":
            self.graph.update(generated_sparql)
            res = "Successfully inserted triples into the graph."
        else:
            raise ValueError("Unsupported SPARQL query type.")

        chain_result: Dict[str, Any] = {self.output_key: res}
        if self.return_sparql_query:
            chain_result[self.sparql_query_key] = generated_sparql
        return chain_result