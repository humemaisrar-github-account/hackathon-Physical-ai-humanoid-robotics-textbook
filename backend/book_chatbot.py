#!/usr/bin/env python3
"""
Book-based Chatbot using OpenAI Agents SDK with OpenRouter.

This script implements a chatbot that answers questions based only on provided book content.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Any


class BookChatbot:
    """
    Book-based chatbot using OpenAI Agents SDK with OpenRouter.

    The agent answers questions ONLY using provided book content.
    No external knowledge or hallucinations allowed.
    """

    def __init__(self):
        """
        Initialize the book chatbot with OpenRouter configuration.
        """
        # Load environment variables
        load_dotenv()

        # Get the OpenRouter API key
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")

        # Configure OpenRouter client
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

        # Model configuration
        self.model = "mistralai/devstral-2512:free"

        # System instructions for the agent
        self.system_prompt = """You are a helpful study assistant for a book. Answer questions STRICTLY based on the provided book content only. Do not generate answers from general knowledge. If the answer is not found in the book content, reply clearly: 'This information is not available in the book.' Keep responses short, clear, and professional. Use simple English. Do not use emojis in responses."""

    def get_response(self, question: str, context: str = None) -> str:
        """
        Get response from the agent based on the question and optional context.

        Args:
            question: The user's question
            context: Optional context from the book

        Returns:
            The agent's response
        """
        # Prepare the messages for the API call
        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        # Add context if provided
        if context:
            messages.append({
                "role": "user",
                "content": f"Book content:\n{context}\n\nQuestion: {question}\n\nAnswer strictly using the book content above."
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Question: {question}\n\nAnswer based on book content only. If not found, say 'This information is not available in the book.'"
            })

        try:
            # Call the OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for more consistent responses
                max_tokens=500
            )

            # Extract the response
            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            # Handle any errors
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                return "Rate limit exceeded. Please wait a moment before asking another question."
            return "Error generating response from the agent."

    def chat(self):
        """
        Interactive chat loop for the book chatbot.
        """
        print("Book Study Assistant - Ask questions about the book content")
        print("Type 'quit' to exit\n")

        while True:
            user_input = input("Your question: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not user_input:
                continue

            response = self.get_response(user_input)
            print(f"Assistant: {response}\n")


def main():
    """
    Main function to run the book chatbot.
    """
    try:
        # Initialize the chatbot
        chatbot = BookChatbot()

        # Run the interactive chat
        chatbot.chat()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please make sure OPENROUTER_API_KEY is set in your environment.")
    except Exception as e:
        print(f"Error running the chatbot: {e}")


if __name__ == "__main__":
    main()