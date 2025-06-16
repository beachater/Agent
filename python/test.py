import requests
import json

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        # "HTTP-Referer": "<YOUR_SITE_URL>", # Optional
        # "X-Title": "<YOUR_SITE_NAME>",    # Optional
    },
    data=json.dumps({
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "messages": [
            {
                "role": "user",
                "content": "What is the meaning of life?"
            }
        ],
    })
)

# Print the response in JSON format
try:
    result = response.json()
    print(json.dumps(result, indent=2))
except json.JSONDecodeError:
    print("Failed to parse JSON response:")
    print(response.text)
