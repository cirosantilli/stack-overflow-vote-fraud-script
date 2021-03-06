/*
Login and upvote and answer.

Try to keep this as small as possible
as it is insane and relies on PhantomJS libs like fs.

I've regretted using CasperJS: too hard to understand the API.
Should have gone with straight PhantomJS or Zombie.

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
/*
Human verification on stackoverflow.com/captcha. This has never happeneded so far with this script.

Sometimes, Stack Overflow asks you if you are not a robot out of the blue if it notices a weird voting pattern,
and asks you to solve a CAPTCHA.

Of course, there is a limit to how much SO can do this, or real users will be too much annoyed.

They URL seems to be fixed at:

- <http://stackoverflow.com/captcha>

Related threads:

- <http://meta.stackoverflow.com/questions/302980/why-stack-overflow-repeatedly-asks-me-if-im-a-robot>
- <http://meta.serverfault.com/questions/854/why-does-serverfault-as-well-as-stackoverflow-etc-asks-for-captcha-so-often>
- <http://meta.stackexchange.com/questions/143455/i-am-not-a-robot>
- <http://meta.stackexchange.com/questions/153561/human-verification-page-not-loading-in-china>
- <http://meta.stackexchange.com/questions/2167/increase-captcha-threshold-for-post-editing>
- <http://meta.stackexchange.com/questions/1343/how-often-do-captchas-appear>
- <http://meta.stackexchange.com/questions/244638/please-use-the-new-recaptcha-on-the-human-verification-dialog>
- <http://meta.stackexchange.com/questions/113974/are-there-some-tips-to-skip-the-human-check>
- <http://meta.stackoverflow.com/questions/281597/how-do-you-answer-the-human-verification>
- <http://meta.stackoverflow.com/questions/294480/why-is-human-verification-required-to-do-a-search>
- <http://meta.stackexchange.com/questions/253524/why-am-i-being-redirected-to-a-captcha-when-i-am-just-searching/253526#253526>
 * */
var exit_status_human_verification = 67
/*
Blacklisted IPs
https://support.cloudflare.com/hc/en-us/articles/203366080-Why-do-I-see-a-captcha-or-challenge-page-Attention-Required-trying-to-visit-a-site-protected-by-CloudFlare-as-a-site-visitor-
The page is like this: <https://github.com/cirosantilli/cloudfare-attention-required>
*/
var exit_status_cloudfare_attention_required = 68

var fs = require('fs');
var casper = require('casper').create({
  logLevel: 'debug',
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
var current_dir = casper.cli.get(5)
var cookie_dir = current_dir + '/cookies'
var log_dir = current_dir + '/logs'

var cookie_path = cookie_dir + '/' + user_id
var question_url = domain + 'questions/' + question_id

var last_response

casper.start()

if (fs.isFile(cookie_path)) {
  phantom.cookies = JSON.parse(fs.read(cookie_path));
}

/*
To help debugging CloudFare.
TODO: if I turn this on, it does not recognize CloudFare!
*/
/*
casper.thenOpen('http://checkip.amazonaws.com/', function() {
  this.echo('IP = ' + this.getHTML());
});
*/

casper.thenOpen(question_url, function(response) {

  last_response = response
  /* Ensure that we are logged in. */
  if (this.exists('.topbar .login-link')) {
    this.open(domain + 'users/login')
    this.wait(5000 + Math.floor(Math.random() * 10000));
    this.fill('form#login-form', {
      email: email,
      password: password
    }, true);
    /*
    TODO use redirect parameters instead like a normal user would:
    users/login?ssrc=head&returnurl=http%3a%2f%2fstackoverflow.com%2fquestions%2f33767237%2fa-hello-world-c-program-compiled-by-mingw-w64-spawns-one-more-short-lived-thre
    Doesn't matter much since we will use mostly cookie login.
    */
    this.wait(5000 + Math.floor(Math.random() * 10000));
    this.open(question_url, function(response) {
      last_response = response
    });
  }
  /* undefined */
  if (last_response.status === undefined || last_response.status === 404) {
    fs.write(log_dir + '/' + user_id + '-' + answer_id + '.html', this.getPageContent(), 'w');
    /* TODO To debug checkip on. */
    this.echo('getTitle = ' + this.getTitle())
    if (this.getTitle() == 'Attention Required! | CloudFlare') {
      this.exit(exit_status_cloudfare_attention_required)
      /*
      Using an else here because I'm unable to understand how exit works.
      the bypass does not prevent the next exit from overwriding the first one:
      https://github.com/n1k0/casperjs/issues/193
      */
    } else {
      this.exit(exit_status_404);
    }
    this.bypass(1)
  } else {
    /* TODO check if "Human Verification - Stack Overflow"*/
    /*
    TODO: right now we don't differentiate answers deleted
    since dump from the robot check page (which should generate an email).
    There were about 500k deleted answers since dump, out of 17M total,
    so it does not matter statistically.
    */

    /* Wait some random interval to "read" the answer. */
    this.wait(5000 + Math.floor(Math.random() * 10000));
    this.click('#answer-' + answer_id + ' .vote-up-off')
    this.wait(upvote_sleep);
    fs.write(cookie_path, JSON.stringify(phantom.cookies), 644);
  }
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
