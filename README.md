[![PyPI version](https://badge.fury.io/py/beatrica-embedding.svg)](https://badge.fury.io/py/beatrica-embedding)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/beatrica-embedding)](https://pepy.tech/project/beatrica-embedding)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue)](https://www.linkedin.com/in/eugene-evstafev-716669181/)

# Beatrica Embedding

`beatrica-embedding` is a Python package designed to embed and analyze code changes in git repositories, utilizing Language Learning Models (LLMs) for enhanced insights. It allows seamless switching between different LLMs, making it highly adaptable for various code analysis needs.

## Installation

To install `beatrica-embedding`, use pip:

```bash
pip install beatrica-embedding
```

## Usage

`beatrica-embedding` offers a flexible way to analyze commit changes and generate insights using different LLMs. Below is an example demonstrating how to extract commit changes from a repository and process them with a chosen LLM.

### Extracting and Embedding Code Changes with LLM

```python
from beatrica_git.recent_change_inspector import BeatricaDiffTracker
from beatrica_embedding.embedding_generator import BeatricaCodeChangeProcessor
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI


# Extract commit changes from a git repository
beatrica_diff_tracker = BeatricaDiffTracker(base_branch="main")

# Analyze the commits
beatrica_diff_tracker.analyze_commits()

# Get the commit changes
commit_changes = beatrica_diff_tracker.commit_changes.items()

# Choose the LLM for processing
# language_model = ChatOpenAI(model_name="gpt-4-0125-preview", api_key=os.getenv("OPENAI_API_KEY"), max_tokens=1000)
language_model = ChatMistralAI(model="mistral-medium-latest", mistral_api_key=os.getenv("MISTRAL_API_KEY"), max_tokens=500)

code_change_processor = BeatricaCodeChangeProcessor(commit_changes, language_model=language_model)

# Process the commit changes
retrieval_chain = code_change_processor.process()

# Example query to analyze the changes
question = "What are the changes in the following code?"
print(question)
result = retrieval_chain(question)

answer = result['answer']
print(answer)
```

## Features

- Flexible integration with multiple LLMs for code change analysis.
- Easy to switch between models like OpenAI's GPT or MistralAI for different levels of analysis.
- Embedding and analyzing commit changes in git repositories for enhanced insights.
- Supports detailed analysis of code changes, leveraging the power of conversational models.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/chigwell/beatrica-embedding/issues).

## License

This project is licensed under the [MIT License](https://choosealicense.com/licenses/mit/).
