from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
import urllib
import json
from datetime import datetime

from django.contrib.auth.models import User
from brassball_web.models import Vote, PayPal, UserMatch, UserDetails, EmailLog, RateLog


def fetch_picture(login_id):
	userbal = User.objects.get(id = login_id)
	userdetail = UserDetails.objects.get(user=userbal)

	query = "SELECT url FROM profile_pic WHERE id= '"+ str(userbal.username) +"'"
	query = urllib.quote(query)
        url = "https://graph.facebook.com/fql?q=" + query
        data = urllib.urlopen(url).read()
        resp = json.loads(data)
        data = resp['data']
        pic_url = data[0]['url']
	userdetail.pic_url = pic_url	
	userdetail.save() 			

def fetch_email(login_id):
	userbal = User.objects.get(id = login_id)
	userdetail = UserDetails.objects.get(user=userbal)

	query = "SELECT username FROM user WHERE uid= '"+ str(userbal.username)+"'"
	query = urllib.quote(query)
        gurl = "https://graph.facebook.com/fql?q=" + query
        data = urllib.urlopen(gurl).read()
        resp = json.loads(data)
        data = resp['data']
        email = data[0]['username'] + '@facebook.com'

	userdetail.email = email	
	userdetail.save() 			


def login_view(request, login_id, email):
    
    pp = User.objects.filter(username=login_id)
    if not pp:
	user = User.objects.create_user(login_id, email, 'password') 
        user = authenticate(username=login_id, password='password')
		
	query = "SELECT url FROM profile_pic WHERE id= '"+ login_id +"'"
	query = urllib.quote(query)
        url = "https://graph.facebook.com/fql?q=" + query
        data = urllib.urlopen(url).read()
        resp = json.loads(data)
        data = resp['data']
        pic_url = data[0]['url']

        url = "https://graph.facebook.com/" + login_id + "?fields=first_name,last_name"
        data = urllib.urlopen(url).read()
        resp = json.loads(data)
        data = resp
        f = data['first_name']
        l = data['last_name']
        user.first_name=f
        user.last_name=l 
	user.save()


	query = "SELECT username FROM user WHERE uid= '"+ login_id +"'"
	query = urllib.quote(query)
        gurl = "https://graph.facebook.com/fql?q=" + query
        data = urllib.urlopen(gurl).read()
        resp = json.loads(data)
        data = resp['data']
        email = data[0]['username'] + '@facebook.com'



	userdetail = UserDetails(email=email, user=user, money="0", credit="0", pic_url = str(pic_url))    	
	userdetail.save()

    username = login_id
    password = 'password'
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
	    return redirect('http://brassballs.biz/')	
        else:
	    error_message = "Disabled Account"
    else:
	 error_message = "Invalid Login"
    
    template = loader.get_template('splash.html')
    context = RequestContext(request, { 
	'error_message': error_message,
    })
    return HttpResponse(template.render(context))

def paymentsuccess(request):
	pp = PayPal(money="10", user=request.user)
	pp.save()
	ud = UserDetails.objects.get(user=request.user)
	ud.money= ud.money + 10
	ud.credit = ud.credit + 10
	ud.save()	
	return redirect('http://brassballs.biz/')	

def paymentfail(request):
	return redirect('http://brassballs.biz/')	

def channel(request):
    return HttpResponse('<script src="//connect.facebook.net/en_US/all.js"></script>')


def logout_view(request):
	logout(request)
	return redirect('http://brassballs.biz/splash')	

def do_mail(request):
    from django.core.mail import send_mail

    send_mail('Subject here', 'Here is the message.', 'gerrithall@gmail.com',
    ['vanhoof.patrick@facebook.com'], fail_silently=False)

 
def index(request):    
    from django.core.mail import send_mail

#    send_mail('Subject here', 'Here is the message.', 'gerrit@alum.swarthmore.edu', ['nicola.azevedo@facebook.com'], fail_silently=False)


    if not request.user.is_authenticated():
	return redirect('http://brassballs.biz/splash')
  
    pp = PayPal.objects.filter(user=request.user)
    paid = pp
    if not paid:
	return redirect('http://brassballs.biz/about')
    
    match_side_a = UserMatch.objects.filter(user=request.user).filter(active=1)
    match_side_a.exclude(user=request.user)
    match_side_b = UserMatch.objects.filter(user2=request.user).filter(active=1)
    match_side_b.exclude(user=request.user)

    requests_outgoing = {}
    requests_outgoing_track = {}
    requests_incoming = []
    active_matches = []
    vote_log = {}
    all_relationships = []
 
    for k in match_side_a:

	durf = UserDetails.objects.get(user=k.user2_id)
	durf2 = User.objects.get(id=k.user2_id)
	if not durf.pic_url:
		durf.pic_url = fetch_picture(k.user2_id)
	if not durf.email:
		durf.email = fetch_email(k.user2_id)
	g = { 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url }
	
	
	s = int(k.user2_id)
	all_relationships.append(s)		
	requests_outgoing[s] = g
	requests_outgoing_track[s] = k.id
    for k in match_side_b:
	durf = UserDetails.objects.get(user=k.user_id)
	durf2 = User.objects.get(id=k.user_id)
	if not durf.pic_url:
		durf.pic_url = fetch_picture(k.user_id)

	g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url }
	s = int(k.user_id)
	all_relationships.append(s)		
	
	if s in requests_outgoing_track:
		g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url, 'current_vote' : get_vote(requests_outgoing_track[s] ), 'counter_id' : requests_outgoing_track[s]}
		active_matches.append(g)
    		
		del requests_outgoing[s]
	else:
		g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url }
		requests_incoming.append(g) 
	
    template = loader.get_template('BB-dashboard.html')
    rand_user_list = UserDetails.objects.order_by('?').exclude(id__in = all_relationships).exclude(user=request.user).exclude(money=0)[:5] 
    
    real_rand = []
    for k in rand_user_list:
	durf = UserDetails.objects.get(user=k.user_id)
	durf2 = User.objects.get(id=k.user_id)
	g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url, 'current_vote' : get_vote(k) }
	s = int(k.user_id)
	real_rand.append(g)	

    top_user_list = UserDetails.objects.order_by('-money')[:5]
    mydeet = UserDetails.objects.get(user=request.user)
    if request.path.find('postvote') > 0:
	voted = 1
    else:
	voted = 0 
    context = RequestContext(request, {
	'paid': paid,
	'money': mydeet.money,
	'rand_user_list': real_rand,
	'top_user_list': top_user_list,
	'active_matches': active_matches,
	'requests_outgoing': requests_outgoing,
	'voted': voted,
	'requests_incoming': requests_incoming,
	'vote_log': vote_log,
    })

     
    return HttpResponse(template.render(context))
    #return HttpResponse("userid %s . " % user_id)

def about(request):
    rand_user_list = UserDetails.objects.order_by('-money')[:5] 
    real_rand = []
    for k in rand_user_list:
	durf = UserDetails.objects.get(user=k.user_id)
	durf2 = User.objects.get(id=k.user_id)
	g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url, 'current_vote' : get_vote(k) }
	s = int(k.user_id)
	real_rand.append(g)	


    template = loader.get_template('rules.html')
    context = RequestContext(request, {
   	'tops': real_rand 
    })
    return HttpResponse(template.render(context))


def splash(request):
    template = loader.get_template('BB-splash-page.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

def leaderboard(request):
    template = loader.get_template('BB-Leaderboard.html')
    rand_user_list = UserDetails.objects.exclude(money=0).order_by('-money')[:20] 
    real_rand = []
    for k in rand_user_list:
	durf = UserDetails.objects.get(user=k.user_id)
	durf2 = User.objects.get(id=k.user_id)
	g = { 'id' : k.id , 'username' : durf2.username , 'first_name' : durf2.first_name, 'last_name' : durf2.last_name, 'user_id' : k.user_id, 'money': k.money , 'pic_url' : durf.pic_url, 'current_vote' : get_vote(k) }
	s = int(k.user_id)
	real_rand.append(g)	

    myid = request.user.id
    context = RequestContext(request, {
    	'leaders': real_rand,
	'myid': myid
	})
    return HttpResponse(template.render(context))

def get_vote(k, y=0):
	try:
		#vl = Vote.objects.filter(usermatch=k, vote_date__range=(datetime.now(), datetime.now() - timedelta(days=1))).order_by('-id')[0]
		now = datetime.now()
		if y:
			vl = Vote.objects.filter(usermatch=k, vote_date__year=now.year, vote_date__month=now.month, vote_date__day=(now.day-y)).order_by('-id')[0]
		else:
			vl = Vote.objects.filter(usermatch=k, vote_date__year=now.year, vote_date__month=now.month, vote_date__day=now.day).order_by('-id')[0]
		#jklfd['dkfld'] = 'flll'	
		return vl.vote
	except:
		return 'split'#split'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
	
def voteall(request):
	val = ''
	for i in request.POST:
		if is_number(i):
			um = UserMatch.objects.get(id = i)
			v = Vote(usermatch = um, vote = request.POST[i])
			v.save()

	return redirect('http://brassballs.biz/postvote')	

def calc_game(request):
	if request.user.id != 1: 
		return HttpResponse("Nope")
	U_orig = {}
	U_new = {}
	dryrun = 1
	y = 0	
	house_pct = .05
	import smtplib
	alert_pending = {}
	alert_incoming = {}
	alert_game = {}
	house = 0
	split_count = 0
	splits = {}
	disable = {}
	dr = ''
	Users = User.objects.all()
	for u in Users:
		ggg = UserDetails.objects.get(id=u.id)
		U_orig[u.id] = ggg.money
		U_new[u.id] = ggg.money
		splits[int(u.id)] = 0

	Match = UserMatch.objects.filter(active=1)
	for m in Match:
		u = User.objects.get(id=m.user_id)
		user = UserDetails.objects.get(id=m.user_id)
		dr = str(user.user_id )
		u2 = User.objects.get(id=m.user2_id)

		durf = User.objects.get(id=m.user_id)
		durf2 = User.objects.get(id=m.user2_id)
		is_matchback = UserMatch.objects.filter(user=u2 , user2_id = u, active=1)
		if is_matchback.count() > 0:
			other_game = is_matchback[0]
			vote_1 = get_vote(m.id, y)
			vote_2 = get_vote(other_game.id, y)
#XXX add fate column (this was stolen, active, pending) and daily summary column (% steal share split)
			if vote_1 == 'split' and vote_2 == 'split':
				st = ["You and " + durf2.first_name + " both shared"]
				splits[int(m.user_id)] = splits[int(m.user_id)] + 1
					
				split_count = split_count + 1
			elif vote_1 == 'steal' and vote_2 == 'split':
				st = ["You successfully stole money from " + durf2.first_name]
				user.money = user.money + (1-house_pct) * m.money
				if dryrun:
					dr = dr + durf.first_name + ' stole from ' + durf2.first_name + '\n'
					U_new[user.id] = U_new[user.id] + (1-house_pct) * m.money
				else:
#XXX log accounting
					user.save()
				disable[m.id] = m.id
			elif vote_1 == 'split' and vote_2 == 'steal':
				st = [durf2.first_name + " stole your money!"]
				user.money = user.money - m.money
				house = house + (house_pct) * m.money
				if dryrun:
					dr = dr + durf.first_name + ' got stolen from ' + durf2.first_name + '\n'
					U_new[user.id] = U_new[user.id] - m.money
				else:
#XXX log accounting
					user.save()
				disable[m.id] = m.id
			elif vote_1 == 'steal' and vote_2 == 'steal':
				st = ["You and " + durf2.first_name + " both tried to steal."]
				user.money = user.money - m.money
				if dryrun:
					dr = dr + durf.first_name + ' and ' + durf2.first_name + 'double stole\n'
					U_new[user.id] = U_new[user.id] - m.money
				else:
					user.save()
				disable[m.id] = m.id
				house = house + .5 * m.money 
			try:
				alert_game[m.user_id].insert(0,st)
			except KeyError:
				alert_game[m.user_id] = [st]
	

		else:
#			m1 = ["Your game with " + durf2.first_name + " " + durf2.last_name + " is still pending."]
#			try: 
#				alert_game[m.user_id].append(m1)
#			except KeyError:			
#				alert_game[m.user_id] = [m1]

			m1 = ["You have a game request from "+ durf.first_name + " " + durf.last_name]
			try: 
				alert_game[m.user2_id].append(m1)
			except KeyError:			
				alert_game[m.user2_id] = [m1]

	for k,v in disable.items():
		m = UserMatch.objects.get(id=k)
		m.active = 0
		m.date_closed = datetime.now() 	
		if dryrun:
			dr = dr + 'something\n in disabling items for ' + str(m.id) + '\n'
		else:
			m.save()

	RateLog(total_money=house, headcount=split_count, effective_rate=house/split_count).save()
	for  k, v in splits.items():
		U = UserDetails.objects.get(id=k)
		U.money = U.money + ((house * (1-house_pct))/split_count)*v
		if dryrun:
			dr = dr + 'saving splits'
			U_new[k] = U_new[k] + ((house * (1-house_pct))/split_count)*v
		else:
			U.save()
		
#$		Active_matches = UserMatch.objects.filter(user_id=k, active=1)			      for m in Active_matches:
			
		## XXX Need to have this update match amounts
		
	for k,i in alert_game.items():
		durf = User.objects.get(id=k)
		durf2 = UserDetails.objects.get(id=k)
			
		msg = 'Hello '+durf.first_name 
		msg = msg + '\n\nThank you for bearing with us as we test Brass Balls.  Here\'s the summary of today\'s game.  Let us know if you suspect anything is incorrect.\n\n'
		blllll = durf2.user_id
		if dryrun:
			amt = U_new[k]
		else:
			amt = durf2.money
		msg = msg + "Here's your activity in Brass Balls for the day.  Your current balance is $"+str(round(amt,2))+" (was $"+str(round(U_orig[durf2.user_id],2))+").  You can play today's game at http://brassballs.biz/ \n\n"
		for j in i:
  		  for k in j:
			msg = msg + "   - " +str(k) + "\n"
		if dryrun:
			dr = dr + msg + '\n'
		else:
	 		server = smtplib.SMTP('localhost')
#		server.sendmail('g@sloan.mit.edu', durf2.email, msg)
			server.sendmail('g@sloan.mit.edu', durf.email, msg)
			EmailLog(recipient=durf.email, message=msg).save()		
			server.quit()
 	
	if dryrun:
		return HttpResponse("<pre>"+dr)
	else:
		return HttpResponse("to "+durf2.email+" \n"+ msg + str(house) + " AND " ) #alert_pending)
	
	subject = "BACKUP REPORT"
	message = "HEY HEY" 
	server = smtplib.SMTP('localhost')
	server.sendmail('sender@host.com', 'gerrithall@gmail.com', message)
	server.quit()

		
	return HttpResponse("SUppps")

def match(request, game_id):
	import smtplib
	user2 = User.objects.get(id = game_id)
		
	um_exists = UserMatch.objects.filter(user=request.user, user2=user2, active=1)
	if um_exists.count() > 0:
		donothing = 1
	else:
		user_match = UserMatch( money='1', user=request.user, user2= user2, active=1, date_closed='2100-01-25 5:04:11', matchback_id = user2.id )
		#XXX add credits here
		user_match.save()

	om = UserMatch.objects.filter(user=user2, user2=request.user,active=1)
	server = smtplib.SMTP('localhost')
	if om.count() > 0:
		msg= user2.first_name + ", \n\n"+request.user.first_name+ " "+request.user.last_name + " has accepted your match.  Visit http://brassballs.biz/ to place your bet."
	else:
		msg= user2.first_name + ", \n\n"+request.user.first_name+ " "+request.user.last_name + " has challenged you to a match of Brass Balls!  Visit http://brassballs.biz/ to accept"
	server.sendmail('g@sloan.mit.edu', user2.email, msg)
	server.quit()

	return redirect('http://brassballs.biz/')	

def vote(request, game_id):
	return HttpResponse("You're voting on %s" % game_id)
