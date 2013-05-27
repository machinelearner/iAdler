from mongoengine import *

class User(DynamicDocument):
    class Meta:
        app_label = 'mbox_processor'

    name = StringField()
    email = StringField()
    #associated_ICA_tags = ListField(StringField(default=["Miscellaneous"]))

    @classmethod
    def uniq(self,list_of_user):
        user_email_hash = {}
        for a_user in list_of_user:
            user_email_hash[a_user.email] = a_user
        return user_email_hash.values()
