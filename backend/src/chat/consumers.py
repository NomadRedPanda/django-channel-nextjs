import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.llm_config import get_client


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print(f"==============url_route========={self.scope["url_route"]}")
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        try:
            LLM_MODEL = "gemini-2.0-flash-exp"
            client = get_client(llm_model=LLM_MODEL)
            completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                "role": "user",
                "content": message
                }
            ]
            )
            response = completion.choices[0].message.content

            # Send message to room group
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat.message", "message": response} )
        
        except Exception as e:
                await self.send(
                text_data=json.dumps({"message":"Something went wrong. Try again"})
                )


    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))


