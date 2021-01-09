#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from flask import render_template, request, Response, flash, redirect, url_for
from models import *
from forms import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'): #nothing to do
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/') #nothing to do
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues') #completed
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  
  areas = Venue.query.distinct('city','state').all()
  for area in areas:
    venues_filter = Venue.query.filter(Venue.state==area.state,Venue.city==area.city).all()
    venues = []
    
    for venue in venues_filter:
      upcoming_shows=0
      past_shows=0
      shows = db.session.query(Venue, Show).join(Show).filter(Venue.id==venue.id).all()
      
      for venue, show in shows:
        if show.start_time > datetime.utcnow():
          upcoming_shows+=1
        else: past_shows+=1

      venues.append({
      'id': venue.id, 
      'name': venue.name,
      'num_upcoming_shows': upcoming_shows
      })

    record = {
      'state': area.state,
      'city': area.city,
      'venues': venues
    }

    data.append(record)
     
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST']) #completed
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  search_query = db.session.query(Venue).filter(Venue.name.ilike('%'+search_term+'%')).all()
  
  data=[]
  
  num_upcoming_shows = 0
  for venue in search_query:
    join = db.session.query(Venue, Show).join(Show).filter(Venue.id == venue.id).all()
    
    for venue, show in join:
      if show.start_time > datetime.utcnow():
        num_upcoming_shows += 1
      
    record = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    
    data.append(record)

  response={
    "count": len(search_query),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>') # completed
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  data_array = []

  venue = Venue.query.filter_by(id=venue_id).first()

  #get every artist, join the venue information to the show information for this artist
  upcoming_shows = []
  past_shows = []
  shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id == venue.id).all()
  for show, artist in shows:
    artist = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    
    if show.start_time > datetime.utcnow():
      upcoming_shows.append(artist)
    else: past_shows.append(artist)
  
  record = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),

  }
  data_array.append(record)

  data = list(filter(lambda d: d['id'] == venue_id, data_array))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET']) #nothing to do
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST']) #completed
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
    data = {}
    try:
      name = request.get_json()['name']
      city = request.get_json()['city']
      state = request.get_json()['state']
      address = request.get_json()['address']
      phone = request.get_json()['phone']
      genres = request.get_json()['genres']
      facebook_link = request.get_json()['facebook']
      image_link = request.get_json()['image_link']
      website = request.get_json()['website']
      seeking_talent = request.get_json()['seeking_talent']
      seeking_description = request.get_json()['seeking_description']
      venue = Venue(
        name=name, city=city, state=state, address=address, phone = phone, 
        genres = genres, facebook_link = facebook_link, image_link=image_link, website=website,
        seeking_talent=seeking_talent, seeking_description=seeking_description
      )
      
      db.session.add(venue)
      db.session.commit()
      data["name"] = venue.name
      data["city"] = venue.city
      data["state"] = venue.state
      data["address"] = venue.address
      data["phone"] = venue.phone
      data["genres"] = venue.genres
      data["facebook_link"] = venue.facebook
      data["image_link"] = venue.image_link
      data["website"] = venue.website
      data["image_link"] = venue.seeking_talent
      data["image_link"] = venue.seeking_description
      flash('message')
    except:
      db.session.rollback()
    finally:
      db.session.close()
      flash('message')
    flash('message')
    #return render_template('pages/home.html')
    return redirect(url_for("index"))
  # TODO: modify data to be the data object returned from db insertion
  
    # on successful db insert, flash success
   # flash('Venue ' + data['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
   # flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    

@app.route('/venues/<venue_id>', methods=['DELETE']) #completed
def delete_venue(venue_id):
  delete_venue = Venue.query.filter_by(id=venue_id).first()
  try:
    db.session.delete(delete_venue)
    db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()
  
  
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/venues.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists') #completed
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.all()
  for artist in artists:
    record={
      "id": artist.id,
      "name": artist.name
    }
    data.append(record)
    
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST']) #completed
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  search_query = db.session.query(Artist).filter(Artist.name.ilike('%'+search_term+'%')).all()
  
  data=[]
  
  num_upcoming_shows = 0
  for artist in search_query:
    join = db.session.query(Artist, Show).join(Show).filter(Artist.id == artist.id).all()
    
    for artist, show in join:
      if show.start_time > datetime.utcnow():
        num_upcoming_shows += 1
      
    record = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows
    }
    
    data.append(record)

  response={
    "count": len(search_query),
    "data": data
  }

  
  response_old={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>') #completed
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }

  data_array = []
  
  artists = Artist.query.all()
  for artist in artists:
    #get every artist, join the venue information to the show information for this artist
    upcoming_shows = []
    past_shows = []
    shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id == artist.id).all()
    for show, venue in shows:
      venue = {
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
      }
      
      if show.start_time > datetime.utcnow():
        upcoming_shows.append(venue)
      else: past_shows.append(venue)
      
    record = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    data_array.append(record)

  data = list(filter(lambda d: d['id'] == artist_id, data_array))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) #completed
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  
  form = ArtistForm(
    name=artist.name,
    state=artist.state,
    city=artist.city,
    phone=artist.phone,
    genres=artist.genres,
    facebook_link=artist.facebook_link,
    image_link=artist.image_link,
    website=artist.website,
    seeking_venue=artist.seeking_venue,
    seeking_description=artist.seeking_description
    )
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST']) #completed
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter_by(id=artist_id).first()
    try:
      artist.name = request.get_json()['name']
      artist.city = request.get_json()['city']
      artist.state = request.get_json()['state']
      artist.phone = request.get_json()['phone']
      artist.genres = request.get_json()['genres']
      artist.facebook_link = request.get_json()['facebook']
      artist.image_link = request.get_json()['image_link']
      artist.website = request.get_json()['website']
      artist.seeking_venue = request.get_json()['seeking_venue']
      artist.seeking_description = request.get_json()['seeking_description']
            
      db.session.commit()
      flash('message')
      print("everything fine")
    except:
      print("something went wrong")
      db.session.rollback()
    finally:
      
      db.session.close()
      flash('message')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET']) #completed
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  
  form = VenueForm(
    name=venue.name,
    state=venue.state,
    city=venue.city,
    address=venue.address,
    phone=venue.phone,
    genres=venue.genres,
    facebook_link=venue.facebook_link,
    image_link=venue.image_link,
    website=venue.website,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
    )
  
  
  venue_old={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST']) #completed
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter_by(id=venue_id).first()
    try:
      venue.name = request.get_json()['name']
      venue.city = request.get_json()['city']
      venue.state = request.get_json()['state']
      venue.address = request.get_json()['address']
      venue.phone = request.get_json()['phone']
      venue.genres = request.get_json()['genres']
      venue.facebook_link = request.get_json()['facebook']
      venue.image_link = request.get_json()['image_link']
      venue.website = request.get_json()['website']
      venue.seeking_talent = request.get_json()['seeking_talent']
      venue.seeking_description = request.get_json()['seeking_description']
            
      db.session.commit()
      flash('message')
    except:
      db.session.rollback()
    finally:
      db.session.close()
      flash('message')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET']) #nothing to do
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST']) #completed
def create_artist_submission():

    data = {}
    try:
      name = request.get_json()['name']
      city = request.get_json()['city']
      state = request.get_json()['state']
      phone = request.get_json()['phone']
      genres = request.get_json()['genres']
      facebook_link = request.get_json()['facebook']
      image_link = request.get_json()['image_link']
      website = request.get_json()['website']
      seeking_venue = request.get_json()['seeking_venue']
      seeking_description = request.get_json()['seeking_description']
      artist = Artist(
        name=name, city=city, state=state, phone = phone, 
        genres = genres, facebook_link = facebook_link, image_link=image_link,
        website = website, seeking_venue = seeking_venue, seeking_description=seeking_description)
      
      db.session.add(artist)
      db.session.commit()
      data["name"] = artist.name
      data["city"] = artist.city
      data["state"] = artist.state
      data["phone"] = artist.phone
      data["genres"] = artist.genres
      data["facebook_link"] = artist.facebook_link
      data["image_link"] = artist.image_link
      data["website"] = artist.website
      data["seeking_venue"] = artist.seeking_venue
      data["seeking_description"] = artist.seeking_description
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
    finally:
      db.session.close()
      
    
    return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') #completed
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data=[]

  shows = Show.query.distinct('venue_id','artist_id').all()
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist =  Artist.query.filter_by(id=show.artist_id).first()
    
    record={
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    data.append(record)
    
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create') #nothing to do
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST']) #completed
def create_show_submission():
  data = {}
  try:
    venue_id = request.get_json()['venue_id']
    artist_id = request.get_json()['artist_id']
    start_time = request.get_json()['start_time']
    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
