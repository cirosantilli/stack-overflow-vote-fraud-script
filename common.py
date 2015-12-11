import csv
import datetime
import sqlite3
import os.path

# Contains the data as the XML inputs (or a subset of it),
# with identical column names, but in a format that is more reusable.
dump_database_path = 'dump.sqlite3'

script_directory = os.path.dirname(os.path.realpath(__file__))

# Contains the which votes should be done by which bot.
schedule_database_path = os.path.join(script_directory, 'schedule.sqlite3')
schedule_database_create_query = """
CREATE TABLE IF NOT EXISTS votes (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    answer_id INT NOT NULL,
    question_id INT NOT NULL,
    vote_time TIMESTAMP DEFAULT NULL,
    script_status INT DEFAULT NULL
);"""
def schedule_ndays():
    return (datetime.date(2017, 1, 1) - datetime.datetime.utcnow().date()).days

vote_script_path = os.path.join(script_directory, 'vote.js')

max_votes_per_day = 30

users_csv_path = os.path.join(script_directory, 'users.csv')
users_csv_user_id_col = 0
users_csv_user_email_col = 1
users_csv_user_password_col = 2
user_id_off = -1
def iterate_users():
    with open(users_csv_path, 'r') as f:
        for row in csv.reader(f):
            yield row

def io_connections_and_cursors():
    input_connection = sqlite3.connect(dump_database_path)
    input_connection.row_factory = sqlite3.Row
    input_cursor = input_connection.cursor()
    output_connection = sqlite3.connect(schedule_database_path)
    output_cursor = output_connection.cursor()
    output_cursor.execute(schedule_database_create_query)
    return input_connection, input_cursor, output_connection, output_cursor 

def commit_and_closeclose_io_connections(input_connection, output_connection):
    input_connection.commit()
    input_connection.close()
    output_connection.commit()
    output_connection.close()

def next_output_id(output_cursor):
    return next(output_cursor.execute('SELECT COALESCE(MAX(Id),0) FROM votes;'))[0] + 1

Posts_PostTypeId_Question = 1
Posts_PostTypeId_Answer = 2

Votes_VoteTypeId_AcceptedByOriginator = 1
Votes_VoteTypeId_UpMod = 2
Votes_VoteTypeId_DownMod = 3
Votes_VoteTypeId_Offensive = 4
Votes_VoteTypeId_Favorite = 5
Votes_VoteTypeId_Close = 6
Votes_VoteTypeId_Reopen = 7
Votes_VoteTypeId_BountyStart = 8
Votes_VoteTypeId_BountyClose = 9
Votes_VoteTypeId_Deletion = 10
Votes_VoteTypeId_Undeletion = 11
Votes_VoteTypeId_Spam = 12
Votes_VoteTypeId_InformModerator = 13

anatomy = {
    'badges': {
        'Id': 'INTEGER',
        'UserId': 'INTEGER',
        'Name': 'TEXT',
        'Date': 'DATETIME',
    },
    'comments': {
        'Id': 'INTEGER',
        'PostId': 'INTEGER',
        'Score': 'INTEGER',
        'Text': 'TEXT',
        'CreationDate': 'DATETIME',
        'UserId': 'INTEGER',
        'UserDisplayName': 'TEXT'
    },
    'posts': {
        'Id': 'INTEGER PRIMARY KEY',
        'PostTypeId': 'INTEGER',
        'ParentId': 'INTEGER', # Only present if PostTypeId is 2.
        #'AcceptedAnswerId': 'INTEGER', # Only present if PostTypeId is 1.
        #'CreationDate': 'DATETIME',
        'Score': 'INTEGER',
        'ViewCount': 'INTEGER',
        #'Body': 'TEXT',
        'OwnerUserId': 'INTEGER', # Present only if user has not been deleted.
        'OwnerDisplayName': 'TEXT',
        #'LastEditorUserId': 'INTEGER',
        #'LastEditorDisplayName': 'TEXT',
        #'LastEditDate': 'DATETIME',
        #'LastActivityDate': 'DATETIME',
        'CommunityOwnedDate': 'DATETIME', # Present only if post is community wikied.
        #'Title': 'TEXT',
        'Tags': 'TEXT',
        #'AnswerCount': 'INTEGER',
        #'CommentCount': 'INTEGER',
        #'FavoriteCount': 'INTEGER',
        #'ClosedDate': 'DATETIME', # Present only if post is closed.
    },
    'votes': {
        'Id': 'INTEGER',
        'PostId': 'INTEGER',
        'UserId': 'INTEGER',
        'VoteTypeId': 'INTEGER',
        'CreationDate': 'DATETIME',
        'BountyAmount': 'INTEGER'
    },
    'posthistory': {
        'Id': 'INTEGER',
        'PostHistoryTypeId': 'INTEGER',
        'PostId': 'INTEGER',
        'RevisionGUID': 'INTEGER',
        'CreationDate': 'DATETIME',
        'UserId': 'INTEGER',
        'UserDisplayName': 'TEXT',
        'Comment': 'TEXT',
        'Text': 'TEXT'
    },
    'postlinks': {
        'Id': 'INTEGER',
        'CreationDate': 'DATETIME',
        'PostId': 'INTEGER',
        'RelatedPostId': 'INTEGER',
        'PostLinkTypeId': 'INTEGER',
        'LinkTypeId': 'INTEGER'
    },
    'users': {
        'Id': 'INTEGER',
        'Reputation': 'INTEGER',
        'CreationDate': 'DATETIME',
        'DisplayName': 'TEXT',
        'LastAccessDate': 'DATETIME',
        'WebsiteUrl': 'TEXT',
        'Location': 'TEXT',
        'Age': 'INTEGER',
        'AboutMe': 'TEXT',
        'Views': 'INTEGER',
        'UpVotes': 'INTEGER',
        'DownVotes': 'INTEGER',
        'EmailHash': 'TEXT',
        'AccountId': 'INTEGER',
        'ProfileImageUrl': 'TEXT'
    },
    'tags': {
        'Id': 'INTEGER',
        'TagName': 'TEXT',
        'Count': 'INTEGER',
        'ExcerptPostId': 'INTEGER',
        'WikiPostId': 'INTEGER'
    }
}

def upvotable_answer(table_name='posts'):
    return """
""".format(table_name)
