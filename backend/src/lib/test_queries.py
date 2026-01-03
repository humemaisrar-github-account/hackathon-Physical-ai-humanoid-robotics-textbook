"""
Predefined test queries for validating retrieval quality and performance.
"""

# List of 10 predefined test queries
TEST_QUERIES = [
    "What is artificial intelligence?",
    "Explain machine learning concepts",
    "What are neural networks?",
    "How does deep learning work?",
    "What is natural language processing?",
    "Explain computer vision",
    "What is reinforcement learning?",
    "How do transformers work?",
    "What is data preprocessing?",
    "Explain model evaluation metrics"
]

# Expected topics or concepts that should be covered by the queries
EXPECTED_TOPICS = {
    "artificial intelligence",
    "machine learning",
    "neural networks",
    "deep learning",
    "natural language processing",
    "computer vision",
    "reinforcement learning",
    "transformers",
    "data preprocessing",
    "model evaluation"
}

# Test query configurations with expected filters
TEST_QUERY_CONFIGS = [
    {
        "query": "What is artificial intelligence?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["artificial", "intelligence", "AI"]
    },
    {
        "query": "Explain machine learning concepts",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["machine", "learning", "algorithm"]
    },
    {
        "query": "What are neural networks?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["neural", "network", "perceptron"]
    },
    {
        "query": "How does deep learning work?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["deep", "learning", "layers"]
    },
    {
        "query": "What is natural language processing?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["natural", "language", "processing", "NLP"]
    },
    {
        "query": "Explain computer vision",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["computer", "vision", "image", "recognition"]
    },
    {
        "query": "What is reinforcement learning?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["reinforcement", "learning", "agent", "reward"]
    },
    {
        "query": "How do transformers work?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["transformer", "attention", "mechanism"]
    },
    {
        "query": "What is data preprocessing?",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["data", "preprocessing", "cleaning"]
    },
    {
        "query": "Explain model evaluation metrics",
        "top_k": 3,
        "filters": {},
        "expected_keywords": ["model", "evaluation", "accuracy", "precision", "recall"]
    }
]