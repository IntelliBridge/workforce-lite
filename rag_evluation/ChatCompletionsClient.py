import requests
import json


class ChatCompletionsClient:
    def __init__(self, 
                 bearer_token=None,
                 base_url="http://localhost:3000"
                 ):
        """
        Initializes the ChatCompletionsClient instance.

        :param base_url: The base URL of the API (e.g., "http://localhost:3000")
        :param bearer_token: The bearer token for authentication (optional)
        :param cookies: A dictionary of cookies to send with requests (optional)
        """
        self.base_url = base_url
        self.bearer_token = bearer_token

    def chat_with_collection(self, 
                             model, 
                             query, 
                             collection_id, 
                             collection_name):

        url = self.base_url + '/api/chat/completions'

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "stream": True,
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ],
            "files": [
                {
                    "id": collection_id, #"56f1185e-72b4-4ca9-bb53-94606f437f87",
                    "name": collection_name, #"breif_document",
                    "type": "collection"
                }
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, stream=True)
        except Exception as e:
            print("Failed to send payload:")
            print(payload)
            print(e)

        msg = ""
        for x in response.iter_content():
            msg = msg + x.decode('utf-8')

        # The chunks are seperated by a double carriage return.
        # The first is the reference docs.
        chunks = msg.split('\n\n')
        ref = json.loads(chunks.pop(0)[6:])

        answer = ""
        for chunk in chunks:
            try:
                answer = answer + json.loads(chunk[6:])['choices'][0]['delta']['content']
            except Exception as e:
                print("Failed to parse :")
                print(chunk)
                print(e)

        return ref, answer


