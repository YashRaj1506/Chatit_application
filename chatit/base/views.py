from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse
from .models import Room , Topic
from .forms import RoomForm


# rooms = [
#     {'id':1, 'name':'Lets learn python'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Frontend  developers'},
# ]


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #checking if q is empty or not and prividing value according to it #else '' measn q is going to be empty

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | #this icontains helps us in making half room searches and get the value like for py you get pytho room
        Q(name__icontains=q) | #helps to seach things by the username who cretaed that room
        Q(description__icontains=q)
        ) #gives all the room in the variable
    
    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk) #with the help of id we brought back one whole single row
    context = {'room' : room}
    return render(request, 'base/room.html',  context)

def createRoom(request):
    form = RoomForm()


    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') #using name parameter 
        
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})