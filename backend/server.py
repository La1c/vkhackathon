import vk_api
from flask import Flask, request, jsonify

class VKYAW(object):
    """VK Yet Another Wrapper"""
    
    def __init__(self):
        login, password = '+79111747421', 'z[jxecnfnmevysv'
        vk_session = vk_api.VkApi(login=login, password=password)

        try:
            vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            pass

        self.vk = vk_session.get_api()
        self.tools = vk_api.VkTools(vk_session)
    
    def get_users_info(self, ids):
        ids_string = str(ids)[1:-1]
        users = self.vk.users.get(user_ids=ids_string, fields=["photo_100"])
        return [{"id" : e.get("id"), 
                 "name" : e.get("first_name") + " " + e.get("last_name"), 
                 "photo" : e.get("photo_100")} for e in users]

    def get_event_all(self, event_name):
        event_id = self.vk.groups.getById(group_ids=event_name)[0].get('id')
        event_members = self.tools.get_all('groups.getMembers', 1000, {'group_id': event_id}).get('items')
        return self.get_users_info(event_members)


wrapper = VKYAW()
app = Flask(__name__)
        
@app.route('/compaignons', methods=['GET'])
def get_compaignons():
    user_id = request.args.get('user_id', '')
    event_name = request.args.get('event_name', '')

    response = wrapper.get_event_all(event_name)

    return jsonify(response)

if __name__ == "__main__":
    app.run()