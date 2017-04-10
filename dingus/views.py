from django.shortcuts import render, redirect

def home(request):
    return redirect('https://discordapp.com/oauth2/authorize?client_id=300518336008159232&scope=bot&permissions=1110957121')
