#!/usr/bin/env python

"""
Preprocessing step that transforms raw XML inputs from the data dump into sqlite databases.

This is done because a database is a format that is much more efficient to query and modify.

The sqlite database does not contain any extra data derived from the XML, and may ommit some columns.

This script takes a long time to run.

Ideally, we would be able to index all columns so created to speed up schedule generation.
But don't do it, it is impossibly slow.
http://stackoverflow.com/questions/15778716/sqlite-insert-speed-slows-as-number-of-records-increases-due-to-an-index
"""

import sqlite3
import os
import xml.etree.cElementTree as etree

import common

def xml_to_sqlite(xml_file_path,
            output_file_path,
            table_name,
            anatomy):
    db = sqlite3.connect(os.path.join(output_file_path))
    db.execute('CREATE TABLE IF NOT EXISTS {} ({})'.format(
        table_name,
        ', '.join(['{} {}'.format(name, type)
            for name, type in anatomy.items()])))
    anatomy_column_names = anatomy.keys()
    with open(xml_file_path) as xml_file:
        tree = etree.iterparse(xml_file)
        i = 0
        for events, row in tree:
            # Filter out columns that may have been
            # commented out of the anatomy.
            row_attributes = {key: value
                    for (key, value)
                    in row.attrib.iteritems()
                    if key in anatomy_column_names}
            row_colum_names = row_attributes.keys()
            if row_attributes:
                query = 'INSERT INTO {} ({}) VALUES ({})'.format(
                    table_name,
                    ', '.join(row_colum_names),
                    ('?, ' * len(row_colum_names))[:-2])
                db.execute(query, [row_attributes[key] for key in row_colum_names])
            row.clear()
        db.commit()
        db.close()

if __name__ == '__main__':
    # To restart the database.
    # Without this, we will just append.
    #if os.path.isfile(common.dump_database_path): os.unlink(common.dump_database_path)
    xml_to_sqlite('Posts.xml', common.dump_database_path, 'posts', common.anatomy['posts'])
