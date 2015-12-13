/*
Login and upvote and answer.

Try to keep this as small as possible
as it is insane and relies on PhantomJS libs like fs.

Put as much as possible on a Node.js script.

This is quick and dirty: SO is just rolling it's upvote API now,
which would be the better way to do this.

But it is full of restrictions, and looks like it requires
an associated APP and manual review before giving a token.

So we just impersonate a real user and be done with it.

This script takes a long time to finish, as it does network connections,
and takes some pauses to look more like a human.
*/

/* Parameters. */
var domain = 'https://stackoverflow.com/'
//var domain = 'http://localhost:8000/'
/* TODO find a decent way to get this done. */
var upvote_sleep = 3000

/* The question was deleted since the dump was made. */
var exit_status_404 = 65
/* TODO: the answer was deleted or the post locked. Implement. */
var exit_status_no_upvote_arrow = 66
/* Human verification on /captcha. */
var exit_status_human_verification = 67

var fs = require('fs');
var casper = require('casper').create({
  logLevel: 'debug',
  loadImages: false,
  pageSettings: {
    /* From http://www.useragentstring.com/pages/Firefox/ */
    userAgent: 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
  },
  verbose: true
});

/* CLI parameters. */
var email = casper.cli.get(0)
var password = casper.cli.get(1)
var user_id = casper.cli.get(2)
var question_id = casper.cli.get(3)
var answer_id = casper.cli.get(4)
/*
As an argument because there is no better way to get the full path to this script
http://stackoverflow.com/questions/16769057/how-to-get-currently-executed-file-directory-in-casperjs
*/
var cookie_dir = casper.cli.get(5) + '/'

var cookie_path = cookie_dir + user_id
var question_url = domain + 'questions/' + question_id

var last_response

casper.start()

if (fs.isFile(cookie_path))
  phantom.cookies = JSON.parse(fs.read(cookie_path));

casper.thenOpen(question_url, function(response) {
  last_response = response
  /* Ensure that we are logged in. */
  if (this.exists('.topbar .login-link')) {
    this.thenOpen(domain + 'users/login', function() {
      this.fill('form#login-form', {
        email: email,
        password: password
      }, true);
    });
    /*
    TODO use redirect parameters instead like a normal user would:
    users/login?ssrc=head&returnurl=http%3a%2f%2fstackoverflow.com%2fquestions%2f33767237%2fa-hello-world-c-program-compiled-by-mingw-w64-spawns-one-more-short-lived-thre
    Doesn't matter much since we will use mostly cookie login.
    */
    this.thenOpen(question_url, function(response) {
      last_response = response
    });
  }
  /* undefined */
  if (last_response.status === undefined || last_response.status === 404) {
    this.exit(exit_status_404);
  }

  /* TODO check if "Human Verification - Stack Overflow"*/

  /*
  TODO: right now we don't differentiate answers deleted
  since dump from the robot check page (which should generate an email).
  There were about 500k deleted answers since dump, out of 17M total,
  so it does not matter statistically.
  */

  /* Wait some random interval to "read" the answer. */
  this.wait(5000 + Math.floor(Math.random() * 10000), function() {
    /* Click upvote button and wait a bit for JavaScript to end executing.. */
    this.thenClick('#answer-' + answer_id + ' .vote-up-off', function() {
      this.wait(upvote_sleep, function() {
        fs.write(cookie_path, JSON.stringify(phantom.cookies), 644);
      });
    });
  });
});

/*
Sanity check if we logged in: only we should be able to edit
our own profile, otherwise 404.
*/
/*
casper.thenOpen(domain + 'users/edit/' + user_id, function(response) {
  this.echo(this.getTitle());
});
*/

casper.run();
