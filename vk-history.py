import vk
import time
import json
import argparse


class VkHelper:
    def __init__(self, access_token, sleep_time=0.3):
        self.sleep_time = sleep_time
        self.session = vk.Session(access_token=access_token)
        self.api = vk.API(self.session, v='5.87')

    def get_peers_ids(self, exclude=[]):
        peers_ids = []
        conversations_count = self.api('messages.getConversations',count=0)['count']
        
        for i in range(0, conversations_count, 200):
            conversations = self.api('messages.getConversations',count=200,offset=i)['items']
            for conversation in conversations:
                id = conversation['conversation']['peer']['id']
                if id not in exclude:
                    peers_ids.append(id)
        
        return peers_ids

    def get_history(self, peer_id, separator="\n"):
        history = []
        messages_count = self.api('messages.getHistory', peer_id=peer_id, count=0)['count']
        
        for i in range(0, messages_count, 200):
            time.sleep(self.sleep_time)
            messages = self.api('messages.getHistory', peer_id=peer_id, count=200, offset=i, rev=1)['items']
            
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

    def get_conversations(self, peers_ids):
        conversations = []
        
        for id in peers_ids:
            time.sleep(self.sleep_time)
            history = self.get_history(id)
            
            if len(history) >= 2:
                conversations.append(history)

        return conversations

    def to_file(self, conversations, filename):
        f = open(filename, 'w')
        json.dump(conversations, f, ensure_ascii=False)
        f.close()

def main():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.set_defaults(peers=None)
    parser.add_argument("access_token", help="a user token to run API methods")
    
    # create the parser for the "peers" command
    parser_peers = subparsers.add_parser('peers', help="list peers IDs you have conversed to")
    parser_peers.set_defaults(peers=True)
    
    # create the parser for the "get" command
    parser_get = subparsers.add_parser('get', help="save message history")
    group = parser_get.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="save message history with all the peers you have conversed to")
    group.add_argument("--ids", type=int, nargs='+', help="save message history with the specified peers")
    parser_get.add_argument("--exclude", type=int, nargs='+', default=[], help="exlude message history with the specified peers from an output")
    default_output = time.ctime().replace(" ", "-") + '.json'
    parser_get.add_argument("-o", "--output", metavar="FILENAME", default=default_output, help="set an output file name")
    
    
    # parse the args
    args = parser.parse_args()
    
    helper = VkHelper(args.access_token)
    
    if args.peers:
        ids = helper.get_peers_ids()
        print("IDs:", json.dumps(ids))
    else:
        if args.all:
            ids = helper.get_peers_ids(args.exclude)
        elif args.ids:
            ids = args.ids
            if args.exclude:
                print("Warning! The --exclude argument doesn't exlcude IDs from a user specified list. Please, exclude them manually.")

        start_time = time.time()

        # TODO: Add a progress bar
        conversations = helper.get_conversations(ids)
        helper.to_file(conversations, args.output)

        execution_time = round(time.time() - start_time, 1)
        print("The download took {} seconds.\nSaved to {}".format(execution_time, args.output))


if __name__ == "__main__":
    main()
