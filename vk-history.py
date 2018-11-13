import vk
import time
import json


class VkHelper:
    def __init__(self, access_token, sleep_time=0.3):
        self.sleep_time = sleep_time
        self.session = vk.Session(access_token=access_token)
        self.api = vk.API(self.session, v='5.87')

    def get_peer_ids(self, exclude):
        peer_ids = []
        conversations_count = api('messages.getConversations',count=0)['count']
        
        for i in range(0, conversations_count, 200):
            conversations = api('messages.getConversations',count=200,offset=i)['items']
            for conversation in conversations:
                id = conversation['conversation']['peer']['id']
                if id not in exclude and str(id) not in exclude:
                    peer_ids.append(id)
        
        return peer_ids

    def get_history(self, peer_id, separator="\n"):
        history = []
        messages_count = api('messages.getHistory', peer_id=peer_id, count=0)['count']
        
        for i in range(0, messages_count, 200):
            time.sleep(self.sleep_time)
            messages = api('messages.getHistory', peer_id=peer_id, count=200, offset=i, rev=1)['items']
            
            prev_id = 0
            for j in range(len(messages)):
                id = messages[j]['from_id']
                text = messages[j]['text']
                
                if id == prev_id:
                    history[-1] += separator + text
                else:
                    history.append(text)
                
                prev_id = id

        return history

    def get_conversations(self, peer_ids):
        conversations = []
        
        for id in peer_ids:
            time.sleep(self.sleep_time)
            history = get_history(id)
            
            if len(history) >= 2:
                conversations.append(history)

        return conversations

    def to_file(conversations, filename):
        f = open(filename, 'w')
        json.dump(conversations, f, ensure_ascii=False)
        f.close()
