import json
from channels.generic.websocket import WebsocketConsumer

from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'connected',
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'message_id' in text_data_json:
            message_id = text_data_json['message_id']
        message = text_data_json['message']

        if text_data_json['type'] == 'approve':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'approve_message',
                    'message_id': message_id,
                    'message': message
                }
            )
        elif text_data_json['type'] == 'reject':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'reject_message',
                    'message': message
                }
            )
        elif text_data_json['type'] == 'complete':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'complete_message',
                    'message_id': message_id,
                    'message': message
                }
            )
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
        }))

    def approve_message(self, event):
        message_id = event['message_id']
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'approve',
            'message_id': message_id,
            'message': message,
        }))

    def reject_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'reject',
            'message': message,
        }))

    def complete_message(self, event):
        message_id = event['message_id']
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'complete',
            'message_id': message_id,
            'message': message,
        }))
