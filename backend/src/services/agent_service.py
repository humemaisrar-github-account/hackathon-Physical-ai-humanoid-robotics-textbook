"""
Agent service for the RAG Agent system.

This module provides functionality to interact with OpenRouter's API
to generate responses based on retrieved context.
"""

import logging
import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from typing import List

from src.config.settings import settings
from src.models.agent import RetrievedDocument, AgentResponse


class AgentService:
    """
    Service class for interacting with OpenRouter's API to generate responses based on context.
    """

    def __init__(self):
        """
        Initialize the agent service with OpenRouter configuration.
        """
        self.logger = logging.getLogger(__name__)

        # 🔑 REQUIRED: Configure OpenRouter
        openrouter_api_key = settings.openrouter_api_key
        if not openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in environment or settings")

        # Create the AsyncOpenAI client for OpenRouter
        self.client = AsyncOpenAI(
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Create the model with the OpenRouter client
        self.model = OpenAIChatCompletionsModel(
            model="mistralai/devstral-2512:free",
            openai_client=self.client
        )

        # Create the run configuration
        self.run_config = RunConfig(
            model=self.model,
            model_provider=self.client
        )

        # Create the Agent with proper system instructions (no API calls during creation)
        self.agent = Agent(
            name="Book Study Assistant",
            instructions=(
                "You are a helpful study assistant for a book. Answer questions STRICTLY based on the provided book content only. "
                "Do not generate answers from general knowledge. If the answer is not found in the book content, reply clearly: "
                "'This information is not available in the book.' Keep responses short, clear, and professional. "
                "Use simple English. Do not use emojis in responses."
            ),
            model=self.model
        )

        self.logger.info("Agent service configured with OpenRouter using Agents SDK")

    def generate_response(
        self,
        question: str,
        retrieved_docs: List[RetrievedDocument]
    ) -> AgentResponse:
        """
        Generate a response to the user's question based on the retrieved documents.
        """

        self.logger.info(
            f"Starting agent processing for question: {question[:60]}..."
        )

        try:
            # No documents → early exit
            if not retrieved_docs:
                return AgentResponse(
                    answer="This information is not available in the book.",
                    sources=[],
                    retrieval_metadata={
                        "retrieved_count": 0,
                        "reason": "no_relevant_content"
                    }
                )

            # Build context
            context_text = "\n\n".join(
                f"[Source {i+1}]\n{doc.content}"
                for i, doc in enumerate(retrieved_docs)
            )

            # Prepare the query with context
            full_query = f"""
Book content:
{context_text}

Question: {question}

Answer strictly using the book content above.
"""

            # Use the Agent with Runner to execute the query (API call happens here)
            result = Runner.run_sync(
                self.agent,
                input=full_query,
                run_config=self.run_config
            )

            # Extract the answer from the result
            answer = result.final_output.strip()

            self.logger.info("Agent response generated successfully")

            return AgentResponse(
                answer=answer,
                sources=retrieved_docs,
                retrieval_metadata={
                    "retrieved_count": len(retrieved_docs),
                    "model_used": "mistralai/devstral-2512:free",
                    "reasoning_completed": True
                }
            )

        except Exception as e:
            self.logger.exception("Agent processing failed")

            # Check if it's specifically an API error that we can identify
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                return AgentResponse(
                    answer="Rate limit exceeded. Please wait a moment before asking another question.",
                    sources=retrieved_docs,
                    retrieval_metadata={
                        "retrieved_count": len(retrieved_docs),
                        "error": "rate_limit_exceeded",
                        "reasoning_completed": False
                    }
                )

            return AgentResponse(
                answer="Error generating response from the agent.",
                sources=retrieved_docs,
                retrieval_metadata={
                    "retrieved_count": len(retrieved_docs),
                    "error": str(e),
                    "reasoning_completed": False
                }
            )