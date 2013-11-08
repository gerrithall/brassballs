from django.conf.urls import patterns, url

from brassball_web import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^splash$', views.splash, name='splash'), 
    url(r'^postvote$', views.index, name='index'), 
    url(r'^about$', views.about, name='about'), 
    url(r'^calc_game$', views.calc_game, name='calc_game'), 
    url(r'^(?P<game_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^match/(?P<game_id>\d+)/$', views.match, name='match'),
    url(r'^voteall$', views.voteall, name='voteall'),
    url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/afs/athena.mit.edu/user/g/e/gerrit/Scripts/django/brassballs/brassball_web/static'}),
    url(r'^logout$', views.logout_view, name='logout_view'),
    url(r'^leaderboard$', views.leaderboard, name='leaderboard'),
    url(r'^(?P<login_id>\d+)/(?P<email>.*)/login/$', views.login_view, name='login_view'),
    url(r'^paymentsuccess$', views.paymentsuccess, name='paymentsuccess'),
    url(r'^paymentfail$', views.paymentfail, name='paymentfail'),
    url(r'^channel$', views.channel, name='channel'),
)

