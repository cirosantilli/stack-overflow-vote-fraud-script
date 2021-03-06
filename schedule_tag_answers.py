#!/usr/bin/env python

"""
Naive strategy for testing: upvote all answers, starting from the oldest to the newest.

Use user 1 of users.csv.

Upvotes the same answers for all users if multiple users are scheduled.

This script only appends new votes to the end of the existing schedule.
It does not remove existing votes.
"""

import itertools
import sqlite3

import common

# First user to schedule for 0 based.
first_user_range = 1
# Last user to schedule for, exclusive.
after_last_user_range = 2

total_votes_per_user = common.schedule_ndays() * common.max_votes_per_day
input_connection, input_cursor, output_connection, output_cursor = common.io_connections_and_cursors()
vote_id = common.next_output_id(output_cursor)
post_rows = input_cursor.execute("""
        SELECT answers.* FROM posts AS answers
        INNER JOIN posts AS questions
        WHERE questions.PostTypeId = ?
        AND answers.PostTypeId = ?
        AND answers.ParentId = questions.Id
        AND answers.CommunityOwnedDate IS NULL
        AND questions.Tags LIKE '%<git>%'
        ORDER BY Id ASC
        LIMIT ?;
        """,
        (common.Posts_PostTypeId_Question, common.Posts_PostTypeId_Answer, total_votes_per_user))
for user_row in itertools.islice(common.iterate_users(), first_user_range, after_last_user_range):
    user_id = user_row[common.users_csv_user_id_col]
    user_nvotes = 0
    for post_row in post_rows:
        output_cursor.execute('INSERT INTO votes VALUES (?, ?, ?, ?, NULL, NULL)',
                (vote_id, user_id, post_row['Id'], post_row['ParentId']))
        vote_id += 1
        user_nvotes += 1
    if user_nvotes != total_votes_per_user:
        print('Warning: not enough posts.')
common.commit_and_closeclose_io_connections(input_connection, output_connection)
