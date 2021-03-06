"""
    @file Responsible for handling the individual User class
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_login import UserMixin

#--------------------------------OUR DEPENDENCIES--------------------------------#

class User(UserMixin):
    def __init__(self, userId):
        """
            Custom user class that extends the expected class from LoginManager
            \n@Brief: Initializes a User with the most basic info needed
            \n@Param: userId - The user's unique id
        """
        # store the user's id for use when object is accessed (via 'current_user')
        # they can use the id for more queries
        self.id = int(userId)

        # Can set other accesible info via
        # self.<var> = <arg to constructor>
