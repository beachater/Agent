import requests
import json

# Define the function to send the message to the API
def send_message(message_content):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
        })
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the text from the "choices" field
        response_data = response.json()
        answer = response_data['choices'][0]['message']['content']
        return answer
    else:
        return f"Request failed with status code: {response.status_code}"

# Main loop
while True:
    user_input = input("You: ")

    if user_input.lower() == 'exit':
        print("Exiting the chat...")
        break

    response = send_message(user_input)

    print("Response: \n" + response)
