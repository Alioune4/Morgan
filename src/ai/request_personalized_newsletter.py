from litellm import completion
import os



response = completion(
    model="gemini/gemini-3.5-flash", 
    messages=[{"role": "user", "content": "write code for saying hi from LiteLLM"}]
)

print(response)