# Schedule

Useful information for you to build your own scheduler.

The schedule is an sqlite3 database with a fixed format that determines which votes our bots will do.

The database format is documented at: <http://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede>

The order of the schedule is not important: the schedule runner picks random votes from it to make it harder for Stack Overflow to spot our puppets.

How the fraud detecting algorithm works is not publicly documented:

- <http://meta.stackexchange.com/questions/126829/what-is-serial-voting-and-how-does-it-affect-me>
- <http://meta.stackexchange.com/questions/223519/do-serial-voting-detection-scripts-really-work>

If an account is caught doing voting fraud, it can be removed or suspended, and its votes reversed.

So obviously, never try to benefit yourself, or you take a big risk. Instead, choose some random user to whom you have absolutely no relation.

Remember that we can only do 30 votes per day. Your scheduler script does not have to worry about that, but keep in mind that any attack will take some time.
