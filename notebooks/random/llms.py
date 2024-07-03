# %% Imports

from typing import Mapping, cast

import ollama

# %% Test LLM

response: Mapping = cast(
    Mapping,
    ollama.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": "Label the following tweet as either 1, relating to movies, or 0, not related to movies. Nothing other than '1' or '0': 'I dont know about this movie'",
            },
        ],
    ),
)

print(response["message"]["content"])

# %%
