from django.shortcuts import render


def socket_base(request, template="base.html"):
    context={}
    return render(request, template, context)
