# Schedule

Useful information for you to build your own scheduler.

The database format is documented at: <http://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede>

How the fraud detecting algorithm works is not publicly documented:

- <http://meta.stackexchange.com/questions/126829/what-is-serial-voting-and-how-does-it-affect-me>
- <http://meta.stackexchange.com/questions/223519/do-serial-voting-detection-scripts-really-work>

If an account is caught doing vote fraud, it can be removed or suspended, and it's votes reversed.

Remember that we can only do 30 votes per day. Your scheduler script does not have to worry about that, but keep in mind that any attack will take some time.
