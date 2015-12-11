#!/usr/bin/env python

"""
Naive strategy for testing: upvote random answers.

TODO this is too slow now: we must find a way to do a single database / disk access...

- http://stackoverflow.com/questions/4329396/mysql-select-10-random-rows-from-600k-rows-fast

If only we could have multiple OFFSETs.
"""

import itertools
import random
import sqlite3

import common

nusers = 1

total_votes_per_user = common.schedule_ndays() * common.max_votes_per_day
input_connection, input_cursor, output_connection, output_cursor = common.io_connections_and_cursors()
vote_id = common.next_output_id(output_cursor)
nanswers = next(input_cursor.execute(
        'SELECT COUNT(*) FROM posts WHERE PostTypeId = ?',
        (common.Posts_PostTypeId_Answer,)))[0]
# Second puppet only.
for user_row in itertools.islice(common.iterate_users(), 1, 1 + nusers):
    user_id = user_row[common.users_csv_user_id_col]
    if user_id != common.user_id_off:
        nscheduled_answers = 0
        answer_indexes = set()
        while nscheduled_answers < total_votes_per_user:
            n = random.randint(0, nanswers - 1)
            if n not in answer_indexes:
                answer_indexes.add(n)
                nscheduled_answers += 1
        user_nvotes = 0
        for answer_i in answer_indexes:
            post_row = next(input_cursor.execute(
                    'SELECT * FROM posts WHERE PostTypeId = ? LIMIT 1 OFFSET ?',
                    (common.Posts_PostTypeId_Answer, answer_i)))
            output_cursor.execute('INSERT INTO votes VALUES (?, ?, ?, ?, NULL, NULL)',
                    (vote_id, user_id, post_row['Id'], post_row['ParentId']))
            output_connection.commit()
            vote_id += 1
            user_nvotes += 1
common.commit_and_closeclose_io_connections(input_connection, output_connection)
