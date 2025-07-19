from django.shortcuts import render
from django.core.mail import mail_admins, BadHeaderError

def say_hello(request):
    # try:
    #     mail_admins('Infectious', 'hello', html_message='<h1>Hello</h1>')
    # except BadHeaderError:
    #     pass
    return render(request, 'hello.html', {'name': 'Mosh'})
