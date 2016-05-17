# app.py
from flask import render_template, request
import json

from app import app

from app.clients.instagram_client import InstagramClient
from app.clients.geolocation_client import GeolocationClient
from app.clients.spotify_client import SpotifyClient
from app.clients.twitter_client import TwitterClient
from app.exceptions.media_missing_exception import MediaMissingException
from app.exceptions.no_locations_exception import NoLocationsException
from app.exceptions.no_twitter_account_exception import NoTwitterAccountException
from app.exceptions.rate_limit_exception import RateLimitException
from app.services.user_network_service import UserNetworkService

@app.route('/hello')
def hello():
	return 'Hello world!'


@app.route('/')
def root():
	return render_template('home.html')


@app.route('/profile', methods=['POST'])
def search():

	# get twitter data
	twttr = TwitterClient()
	name = request.form['search']
	no_twitter = False
	screen_name = ''
	twitter_loc = ''
	twitter_des = ''
	hashtags = []
	retweet = []
	photo = []
	profile =[]
	links = []
	t_stats = {}
	animals = {}
	try:
		screen_name = twttr.search_username(name)
		twitter_loc = twttr.user_location(screen_name)
		twitter_des = twttr.user_description(screen_name)
		hashtags = twttr.aggregate_hashtags(screen_name, 3200)
		retweet = twttr.aggregate_retweets(screen_name, 3200)
		photo = twttr.aggregate_photos(screen_name, 1000)
		p_url = twttr.get_user_profile(screen_name)["profile_image_url_https"]
		profile =  [] if "default_profile_images" in p_url else p_url
		links = twttr.search_links(screen_name, ["itunes", "spotify", "sptfy"], 1000)
		t_stats = twttr.get_twitter_stats(screen_name)
		animals = twttr.search_tweets(screen_name, ["cat", "dog", "puppy", "kitten", "puppies"], 100)

	except NoTwitterAccountException:
		no_twitter = True

	# get instagram data
	user_network = UserNetworkService(screen_name)
	insta = InstagramClient()
	geolocation = GeolocationClient()
	search_term = request.form['search']
	username = ''
	media_missing = False
	no_locations = False
	rate_limited = False
	markers = []
	i_stats = {}
	insta_photos = []
	try:
		username = user_network.get_best_instagram_username()
		location_names = insta.get_location_names(username)
		for location in location_names:
			current_marker = {'title': location}
			coordinates = geolocation.find_coordinates(location)
			if coordinates:
				current_marker.update(coordinates)
				markers.append(current_marker)
		insta_photos = insta.aggregate_photos(username)
		if not profile:
			profile = insta.get_user_profile_picture(username)
		i_stats = insta.get_instagram_stats(username)
	except MediaMissingException:
		media_missing = True
	except NoLocationsException:
		no_locations = True
	except RateLimitException:
		rate_limited = True

	# split spotify urls
	spotify = SpotifyClient(links['spotify'])
	spotify_uris = spotify.generate_uris()

	# render template with template variables
	return render_template(
		'profile.html',
		search=name,
		hashtags=hashtags,
		retweet=retweet,
		t_loc=twitter_loc,
		t_desc=twitter_des,
		t_pic=photo,
		i_pic=insta_photos,
		markers=json.dumps(markers),
		media_missing=media_missing,
		no_locations=no_locations,
		no_twitter=no_twitter,
		rate_limited=rate_limited,
		profile=profile,
		links=links,
		spotify_uris=spotify_uris,
		t_stats=t_stats,
		i_stats=i_stats,
		animals=animals
	)


@app.route('/redirect', methods=['GET', 'POST'])
def redirect():
	return render_template('home.html')


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
	query = request.form['query']
	twitter = TwitterClient()
	usernames = twitter.search_usernames(query)
	return json.dumps(usernames)
