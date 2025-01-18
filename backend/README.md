### Installtion

```bash
python -m pip install -U 'channels[daphne]'
```

- Install the Daphne’s ASGI version of the runserve
  `AJHome/settings.py`
  `python
  INSTALLED_APPS = (
  "daphne", #
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.sites",
  ...
  )
  ...
  # Channel
  ASGI_APPLICATION = "AJHome.asgi.application"
  `
- Wrap Django ASGI application
  `AJHome/asgi.py`

  ```python
  import os
  from channels.routing import ProtocolTypeRouter
  from django.core.asgi import get_asgi_application

  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AJHome.settings')

  application = ProtocolTypeRouter({
      "http": get_asgi_application(),
  })
  ```

- when you run `python manage.py runserver` you will see
  `beginning with Starting ASGI/Daphne …`

### Implement a Chat server

- In http request, urls.py -> views.py
- Websocet connection, routing.py -> consumers.py
- Created a consumer that accepts WebSocket connections
  `chat/consumers.py`

  ```python
  # similar to views.py
  import json
  from channels.generic.websocket import WebsocketConsumer

  class ChatConsumer(WebsocketConsumer):
      def connect(self):
          self.accept()

      def disconnect(self, close_code):
          pass

      def receive(self, text_data):
          text_data_json = json.loads(text_data)
          message = text_data_json["message"]

          self.send(text_data=json.dumps({"message": message}))

  ```

  `chat/routing.py`

  ```python
  # similar to urls.py
  from django.urls import re_path
  from . import consumers

  websocket_urlpatterns = [
      re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
  ]
  ```

- Point the main ASGI configuration at the chat.routing module
  `AJHome/asgi.py`

  ```python
  # similar to AJHome/urls.py
      ...

  from chat.routing import websocket_urlpatterns
  application = ProtocolTypeRouter(
      {
          "http": get_asgi_application(),
          "websocket": AllowedHostsOriginValidator(
              AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
          ),
      }
  )

  ```

- Enable a channel layer: to have multiple instances of the same ChatConsumer be able to talk to each other
- Start a Redis server
  `docker run --rm -p 6379:6379 redis:7`
- install channels_redis: make channels knows how to interface with Redis
  `pip install channels_redis`  
   `AJHome/settings.py`

  ```python
  # Channels
  ASGI_APPLICATION = "AJHome.asgi.application"
  #It's possible to have multiple channel layers configured. However most projects will just use a single 'default' channel layer.
  CHANNEL_LAYERS = {
      "default": {
          "BACKEND": "channels_redis.core.RedisChannelLayer",
          "CONFIG": {
              "hosts": [("127.0.0.1", 6379)],
          },
      },
  }

  ```

- Add channel layer to `chat/consumers.py` and make it to asynchronous

  ```python
    import json
    from channels.generic.websocket import AsyncWebsocketConsumer

    class ChatConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
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
            print(f"=======text_data_json====={self.scope["url_route"]}")
            # Send message to room group
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat.message", "message": message} )


        # Receive message from room group
        async def chat_message(self, event):
            message = event["message"]

            # Send message to WebSocket
            await self.send(text_data=json.dumps({"message": message}))
  ```

### Automated Testing

- Add test.py
- add the TEST argument to the DATABASES setting
  ```python
  DATABASES = {
      "default": {
          "ENGINE": "django.db.backends.sqlite3",
          "NAME": BASE_DIR / "db.sqlite3",
          "TEST": {
              "NAME": BASE_DIR / "db.sqlite3",
          },
      }
  }
  ```
