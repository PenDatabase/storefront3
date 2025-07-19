from django.shortcuts import render
from django.core.mail import BadHeaderError
from templated_mail.mail import BaseEmailMessage

def say_hello(request):
    try:
        message = BaseEmailMessage(template_name="emails/hello.html",
                                   context= {"name": "David"})
        message.send(["davideneasatochibueze@gmail.com"])
    except BadHeaderError:
        pass
    return render(request, 'hello.html', {'name': 'Mosh'})
