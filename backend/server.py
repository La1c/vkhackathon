import vk_api
from vk_api.execute import VkFunction
import itertools
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

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

#         self.vk_api = vk_session
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

    def get_event_subs_inter(self, user_id, event_id):
        event_members_iter= self.tools.get_all_iter('groups.getMembers', 1000, {'group_id': event_id})
        coeffs = [(member_id, self.subs_coeff(user_id, member_id)) for member_id in event_members_iter]
        return self.get_users_info([entry[0] for entry in sorted(coeffs, key=lambda entry: entry[1], reverse=True)])

    def get_subs_group_set(self, user_id):
        subscriptions = self.vk.users.getSubscriptions(user_id=user_id)
        return set(subscriptions.get('groups').get('items'))

    def subs_coeff(self, id_one, id_two):
        try:
            set_one = self.get_subs_group_set(id_one)
            set_two = self.get_subs_group_set(id_two)

            # TODO: which denominator should we use?
    #         denom = min(len(set_one), len(set_two)
            denom = (len(set_one) + len(set_two)) / 2

            return len(set_one.intersection(set_two)) / denom

        except vk_api.ApiError as error_msg:
            print(error_msg, id_one, id_two)
            return 0

wrapper = VKYAW()
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/compaignons', methods=['GET'])
@cross_origin()
def get_compaignons():
    user_id = request.args.get('user_id', '')
    event_id = request.args.get('event_id', '')

#     response = wrapper.get_event_all(event_name)
    response = wrapper.get_event_subs_inter(user_id, event_id)

    return jsonify(response)

if __name__ == "__main__":
    app.run()
