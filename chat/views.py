from django.shortcuts import render
# Create your views here.

def lobby(request,other_username):
    return render(request, 'chat/lobby.html',{'other_username': other_username})