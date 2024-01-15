from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Room , Topic, Message
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse


# rooms = [
#     {'id':1, 'name':'Lets learn python'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend  developers'},
# ]

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':                       #we basically get login input
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:                                           #we see if that user exist and if not throw erorr
            user = User.objects.get(username=username)    
        except:
            messages.error(request,'User does not exist')

        user = authenticate(request, username=username, password=password)  #we then authenticate the user

        if user is not None:                           #wethen login the user is user contains the autheenticate value
            login(request, user)  
            return redirect('home')
        
        else:
            messages.error(request, "username or password doesn't exist")

    context={'page' : page}
    return render(request, 'base/login_register.html', context)


def logOutUser(request):
    logout(request)
    return redirect ('home')

def registerPage(request):

    form = UserCreationForm()  #used for basic form input field rendering

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #checking if q is empty or not and prividing value according to it #else '' measn q is going to be empty

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #this icontains helps us in making half room searches and get the value like for py you get pytho room
        Q(name__icontains=q) | #helps to seach things by the username who cretaed that room
        Q(description__icontains=q)
        ) #gives all the room in the variable
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages' : room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk) #with the help of id we brought back one whole single row
    room_messages = room.message_set.all() #here message is the Message model but it is just used as lowercase message.
    participants = room.participant.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user= request.user,
            room = room,
            body=request.POST.get('body')

        )
        room.participant.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room' : room, 'room_messages' : room_messages, 'participants': participants}
    return render(request, 'base/room.html',  context)

def userProfile(request, pk):
    user= User.objects.get(id=pk)
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    context = {'user': user, 'rooms':rooms, 'topics': topics, 'room_messages': room_messages} 
    return render(request, 'base/profile.html', context)

@login_required(login_url='login') #now createroom function can only be accesed if user is authenticated
def createRoom(request):
    form = RoomForm()


    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False) 
            room.host = request.user
            room.save()
            return redirect('home') #using name parameter 
        
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)     

    if request.user != message.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : message})







