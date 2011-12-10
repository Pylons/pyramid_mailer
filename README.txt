pyramid_mailer is a package for sending email from your Pyramid application.

See the documentation at
http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/ for more info.

pyramid_mailer uses code from the Lamson Project (http://lamsonproject.org/)
with permission.  See the LICENSE.txt file for more information.

IMPORTANT: This version has been modified by me in order to get one
features I need in my projects (since I come from a Django background).

The changes are:

1. Now you can specify the mailer type (Mailer, DummyMailer, etc) from
   your project .ini file, for example, in my development.ini file I have:

   mail.mailer = pyramid_mailer.mailer.LoggingMailer

   Here I'm telling that I want my mailers to be instances of
   pyramid_mailer.mailer.LoggingMailer

2. Added LoggingMailer class in pyramid_mailer.mailer module. This mailer
   all it does is log all the messages you send using any of the
   standard mailer methods: send, send_immediately, send_to_queue
   By default the logger used by this class is named `pyramid_mailer` but
   you can change it through the .ini file.
   For example, let's configure the LoggingMailer to send all the messages
   to the console:
   (in my case, I write this in development.ini)

   [app:main]
   ...
   mail.mailer = pyramid_mailer.mailer.LoggingMailer
   ...
   [loggers]
   keys = root, ..., pyramid_mailer
   ...
   [logger_pyramid_mailer]
   level = INFO
   handlers = console
   qualname = pyramid_mailer
   ...

   With that in place, any time you send a message from your views, the
   message will be logged to the console and to the logging of the debug
   toolbar in case you are using it.
   An example of using this mailer in the views:

   from pyramid_mailer import get_mailer
   from pyramid_mailer.message import Message

   def myview(request):
       message = Message(...)
       mailer = get_mailer(request)
       mailer.send(message) # The message is logged
       return {}

