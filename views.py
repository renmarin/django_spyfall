from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.urls import reverse
from .models import Places, Players
from .forms import JoinRoomForm, SetNameForm
from django.http import JsonResponse
from django.contrib import messages

import random
import time

empty_rooms = [str(num) for num in range(0, 101)]

def index(request):

    # session life time if not used
    request.session.set_expiry(21600)  # 6 hours
    # default user's role
    request.session['role'] = 'NoR'

    # redirect user to new random room or manual choosen room with
    if request.method == "POST":
        JoinRoomForm(request.POST)
        SetNameForm(request.POST)

        # button for random new empty room
        if 'new_room' in request.POST and JoinRoomForm(request.POST).is_valid:
            new_random_room_id = random.choice(empty_rooms)
            empty_rooms.remove(new_random_room_id)
            return HttpResponseRedirect(reverse('spyfall:room', args=(new_random_room_id,)))

        # field and button for changing user name
        elif 'user_name' in request.POST and SetNameForm(request.POST).is_valid():
            request.session['user_name'] = request.POST['user_name']
            if request.session['user_name'].startswith("');") or request.session['user_name'].startswith(");"):
                request.session['user_name'] = 'Nice try, Bobby'
            return HttpResponseRedirect(reverse('spyfall:index'))

        # field and button to join only existing rooms
        if JoinRoomForm(request.POST).is_valid():
            request.session['room_number'] = request.POST['room_number']
            if request.POST['room_number'] in empty_rooms\
                    or request.POST['room_number'][0] not in "0123456789"\
                    or int(request.POST['room_number']) > 101:
                messages.error(request, 'Room doesn\'t exist! Try create a new room.' )
                return HttpResponseRedirect(reverse('spyfall:index'))
            return HttpResponseRedirect(reverse('spyfall:room', args=(request.POST['room_number'],)))
    else:
        JoinRoomForm()
        SetNameForm()

    context = {'room_number': request.session.get('room_number'),
               'JoinRoomForm': JoinRoomForm(request.POST),
               'SetNameForm': SetNameForm(request.POST),
               'role': request.session.get('role', 'NoRole'),
               'user_name': request.session.get('user_name', 'NoName'),
               'db': Players.objects.values()
               }

    return render(request, 'spyfall/index.html', context)


def room(request, room_id, _meta_data={}, first_run={str(num): True for num in range(0, 101)}):

    # connect only by using forms
    if request.META.get('HTTP_REFERER') == f'http://127.0.0.1:8000/spyfall/room/{room_id}/':
        pass
    elif request.META.get('HTTP_REFERER') != 'http://127.0.0.1:8000/spyfall/':
        messages.error(request, 'Connect only by using forms!')
        messages.error(request, request.META.get('HTTP_REFERER'))
        return HttpResponseRedirect(reverse('spyfall:index'))

    # set room as 'in usage'
    if room_id in empty_rooms:
        empty_rooms.remove(room_id)

    request.session.set_expiry(21600)

    default_user_names = tuple([f"Max {num}" for num in range(1, 9)])

    # one time setting up room after creating
    if first_run[room_id]:
        first_run[room_id] = False
        places_count = Places.objects.all().count()  # places_count = len(Places.objects.all())
        random_index = random.randint(1, places_count)
        place = Places.objects.get(pk=random_index)
        _meta_data[room_id] = {
            'place': place,
            'users': {},
            'roles': [],
            'start': False,
            'default_user_names': [f"Max {num}" for num in range(1, 9)],
            'start_time': 0,
            'end_time': 0,
            'game_going_on': False
        }

    # set tuple with all possible roles for current place in room
    all_roles_for_room = tuple([row['role'] for row in list(_meta_data[room_id]['place'].roles_set.values())])

    if request.method == "POST":
        # create pool of roles from all roles for current amount of players
        if 'start' in request.POST:
            if _meta_data[room_id]['start'] == True:
                _meta_data[room_id]['start'] = False
                players_db = Players.objects.get(room_id=room_id)
                players_db.refresh_room = True
                players_db.start = False
                players_db.save()
                return HttpResponseRedirect(reverse('spyfall:room', args=(room_id,)))

            # if not enough players show message error
            if len(_meta_data[room_id]['users']) < 2:
                messages.warning(request, 'Need at least 2 players to start a game!')
            else:
                # create new roles pull only for first game start
                if _meta_data[room_id]['users'][request.session['user_name']] == f'NoR {room_id}':
                    index = -1
                    while len(_meta_data[room_id]['roles']) < len(_meta_data[room_id]['users']):
                        _meta_data[room_id]['roles'].append(all_roles_for_room[index])
                        index -= 1
                    random.shuffle(_meta_data[room_id]['roles'])

                # shuffle roles pull and setting timer for game
                _meta_data[room_id]['start'] = True
                _meta_data[room_id]['start_time'] = int(str(time.time())[:14].replace('.', ''))  # time.time()
                if len(_meta_data[room_id]['users']) <= 4:
                    if _meta_data[room_id]['end_time'] == 0:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id]['start_time'] + 390000  # 6.5 min
                    else:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id].get('end_time')
                elif len(_meta_data[room_id]['users']) <= 6:
                    if _meta_data[room_id]['end_time'] == 0:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id]['start_time'] + 450000  # 7.5 min
                    else:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id].get('end_time')
                else:
                    if _meta_data[room_id]['end_time'] == 0:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id]['start_time'] + 510000  # 8.5 min
                    else:
                        _meta_data[room_id]['end_time'] = _meta_data[room_id].get('end_time')

                # JS in html wil auto refresh room for all players in the room by taking info from DB
                players_db = Players.objects.get(room_id=room_id)
                players_db.refresh_room = True
                players_db.start = True
                # to not overwrite databases end_time value for pause mechanic
                if _meta_data[room_id]['end_time'] == _meta_data[room_id]['start_time'] + 390000:
                    players_db.end_time = _meta_data[room_id]['end_time']
                elif _meta_data[room_id]['end_time'] == _meta_data[room_id]['start_time'] + 450000:
                    players_db.end_time = _meta_data[room_id]['end_time']
                elif _meta_data[room_id]['end_time'] == _meta_data[room_id]['start_time'] + 510000:
                    players_db.end_time = _meta_data[room_id]['end_time']
                players_db.save()

                _meta_data[room_id]['game_going_on'] = True

                return HttpResponseRedirect(reverse('spyfall:room', args=(room_id,)))

        # del user name from room's users. if no one left set room free for others
        if 'exit' in request.POST:
            _meta_data[room_id]['users'].pop(request.session.get('user_name'))
            if request.session.get('user_name') in default_user_names:
                _meta_data[room_id]['default_user_names'].insert(0, request.session.get('user_name'))
                del request.session['user_name']

            # if no users in room left add room to empty rooms and reset it state to default
            if not _meta_data[room_id]['users']:
                first_run[room_id] = True
                empty_rooms.append(room_id)
                Players.objects.filter(room_id=room_id).delete()
            else:
                # update database for JS's auto refresh
                player_max = len(all_roles_for_room)
                current_players = len(_meta_data[room_id]['users'])
                players_ratio = f"{current_players}/{player_max}"

                players_db = Players.objects.get(room_id=room_id)
                players_db.names = '<li> ' + ' <li>'.join(_meta_data[room_id]['users'].keys())
                players_db.players = players_ratio
                players_db.save()

            return HttpResponseRedirect(reverse('spyfall:index'))

        # restart room with new place and init code
        elif 'new_game' in request.POST:
            first_run[room_id] = True
            _meta_data[room_id]['start'] = False
            players_db = Players.objects.get(room_id=room_id)
            players_db.refresh_room = True
            players_db.start = False
            players_db.end_time = '0'
            players_db.save()
            # return HttpResponseRedirect(reverse('spyfall:room', args=(room_id,)))

    # check if room has empty spot, if not user get redirected to index page
    if not request.session.get('user_name') or request.session.get('user_name') not in _meta_data[room_id]['users']:
        if len(_meta_data[room_id]['users']) >= len(all_roles_for_room) \
                or _meta_data[room_id]['game_going_on']:  # - 1
            messages.error(request, 'Room has no empty space!')  # 'Room room room!'
            return HttpResponseRedirect(reverse('spyfall:index'))

    # give user new name from default names or use user's existing name for current room;
    request.session['user_name'] = request.session.get('user_name',
                                                       _meta_data[room_id]['default_user_names'][0])
    if request.session.get('user_name') in _meta_data[room_id]['default_user_names']:
        try:
            _meta_data[room_id]['default_user_names'].remove(request.session.get('user_name'))
        except IndexError:
            raise IndexError("Somehow all reserved default names are gone. Do something with it!")

    # give user tmp role and add him to room's users count if game has not started
    if request.session['user_name'] not in _meta_data[room_id]['users'] and not _meta_data[room_id]['start']:
        _meta_data[room_id]['users'][request.session['user_name']] = f'NoR {room_id}'  # request.session['role']

    # give user role after game start
    if _meta_data[room_id]['start']:
        if _meta_data[room_id]['users'][request.session['user_name']] != f'NoR {room_id}':
                request.session['role'] = _meta_data[room_id]['users'][request.session['user_name']]
        else:
            request.session['role'] = _meta_data[room_id]['roles'][-1]
            _meta_data[room_id]['roles'].remove(request.session['role'])
            _meta_data[room_id]['users'][request.session['user_name']] = request.session['role']

    # show ratio of current users to max space in room
    players_ratio = f"{len(_meta_data[room_id]['users'])}/{len(all_roles_for_room)}"

    # DataBase for auto refreshing info on page
    try:
        players_db = Players.objects.get(room_id=room_id)
        players_db.players = players_ratio
        players_db.names = '<li> ' + '<li> '.join(_meta_data[room_id]['users'].keys())
        players_db.save()
    except:
        players_db = Players(room_id=room_id, players=players_ratio,
                             names='<li> ' + '<li> '.join(_meta_data[room_id]['users'].keys()),
                             refresh_room=False, start=False)
        players_db.save()

    context = {'room_id': room_id,
               'players_ratio': players_db.players,
               'place': _meta_data[room_id]['place'],
               'all_roles_for_room': all_roles_for_room,
               'player_name': request.session.get('user_name'),
               'role': request.session.get('role')
                   if _meta_data[room_id]['users'][request.session['user_name']] != f'NoR {room_id}'
                   else 'yet to get',
               'users': _meta_data[room_id]['users'].keys(),
               # 'meta_data': _meta_data[room_id].items(),
               }
    if _meta_data[room_id]['start_time']:
        context['time'] = _meta_data[room_id]['end_time']

    if _meta_data[room_id]['users'][request.session['user_name']] == 'Spy':
        return render(request, 'spyfall/room_spy.html', context)

    _meta_data[room_id]['start'] = players_db.start

    return render(request, 'spyfall/room.html', context)


def control_room(request, room_id, _meta_data={}, first_run={str(num): True for num in range(0, 101)}):
    if first_run[room_id]:
        first_run[room_id] = False
        _meta_data[room_id] = {'ingame': False}

    # POST request
    if request.method == 'POST':
        db = Players.objects.get(room_id=room_id)
        time.sleep(1.4)
        db.refresh_room = False
        db.save()
        return HttpResponse(f'OK - {db.refresh_room}')

    # GET request
    else:
        db = Players.objects.get(room_id=room_id)
        if '.' in db.end_time:
            db.end_time = db.end_time[:10]
            db.save()
        data = {room_id: [db.players, db.names, db.refresh_room, db.start, db.end_time]}
        # pause timer mechanic
        if len(db.end_time) != 13:
            _meta_data[room_id]['ingame'] = False
        if db.start == True:
           _meta_data[room_id]['ingame'] = True
        if db.start == False and _meta_data[room_id]['ingame']:
            if int(time.time()) == int(db.end_time[:10]):
                db.start = False
                db.save()
            elif request.session.get('user_name') == db.names.split('<li>')[1].strip():
                # pause_time = int(1000 / int(db.players[0]))
                # db.end_time = str(int(db.end_time) + pause_time + 100)  # 1 second
                db.end_time = str(int(db.end_time) + 1000)  # 1 second
                db.save()
        return JsonResponse(data)  # serialize and use JSON headers
