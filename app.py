#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask_migrate import Migrate
from sqlalchemy import func
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from db_models import *

# TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration. DONE

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

#DONE
@app.route('/venues')
def venues():
  # TODO: replace with real venues data. DONE
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. DONE
  all_places = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for place in all_places:
    venue_places = Venue.query.filter_by(state=place.state).filter_by(city=place.city).all()
    venue_data = []
    for venue in venue_places:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(
          Show.query.filter(Show.venue_id == 1).filter(Show.start_time > datetime.now()).all())
      })
    data.append({
      "city": place.city,
      "state": place.state,
      "venues": venue_data
    })

  #data=[{
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "venues": [{
  #    "id": 1,
  #    "name": "The Musical Hop",
  #    "num_upcoming_shows": 0,
  #  }, {
  #    "id": 3,
  #    "name": "Park Square Live Music & Coffee",
  #    "num_upcoming_shows": 1,
  #  }]
  #}, {
  #  "city": "New York",
  #  "state": "NY",
  # "venues": [{
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "num_upcoming_shows": 0,
  # }]
  #]
  return render_template('pages/venues.html', areas=data);

#DONE
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. DONE
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  SearchResult = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in SearchResult:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(
        Show.query.filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  response = {
    "count": len(SearchResult),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#DONE
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('errors/404.html')

  upcoming_shows_query = Show.query.join(Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time > datetime.now()).all()
  UpcomingShows = []

  past_shows_query = Show.query.join(Artist).filter(Show.venue_id == venue_id).filter(
    Show.start_time < datetime.now()).all()
  PastShows = []

  for show in past_shows_query:
    PastShows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    UpcomingShows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": PastShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": len(PastShows),
    "UpcomingShows_count": len(UpcomingShows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
#DONE
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  try:
    name = request.form['name']
    city = request.form['city']
    state=request.form['state']
    address=request.form['address']
    phone=request.form['phone']
    image_link=request.form['image_link']
    genres=request.form.getlist('genres')
    facebook_link=request.form['facebook_link']
    website_link=request.form['website_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description=request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link,
    genres=genres, facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent,
    seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead. DONE
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    show = Show.query.filter(Show.venue_id == venue_id).delete()
    venue_name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted.')
  else:
    flash('Venue ' + venue_name + ' was successfully deleted!')

  return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------

#DONE
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

#DONE
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  SearchResult = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []

  for result in SearchResult:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(
        Show.query.filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })

  response = {
    "count": len(SearchResult),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#DONE
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_query = Artist.query.get(artist_id)

  if not artist_query:
    return render_template('errors/404.html')

  PastShows_query = Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time > datetime.now()).all()
  PastShows = []

  for show in PastShows_query:
    PastShows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  UpcomingShows_query = Show.query.join(Venue).filter(Show.artist_id == artist_id).filter(
    Show.start_time > datetime.now()).all()
  UpcomingShows = []

  for show in UpcomingShows_query:
    UpcomingShows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
    "id": artist_query.id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": artist_query.website,
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": artist_query.seeking_venue,
    "seeking_description": artist_query.seeking_description,
    "image_link": artist_query.image_link,
    "past_shows": PastShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": len(PastShows),
    "upcoming_shows_count": len(UpcomingShows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

#DONE
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_query = Artist.query.get(artist_id)

  if artist_query:
    form.name.data = artist_query.name
    form.city.data = artist_query.city
    form.state.data = artist_query.state
    form.phone.data = artist_query.phone
    form.genres.data = artist_query.genres
    form.facebook_link.data = artist_query.facebook_link
    form.image_link.data = artist_query.image_link
    form.website_link.data = artist_query.website
    form.seeking_venue.data = artist_query.seeking_venue
    form.seeking_description.data = artist_query.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id> DONE
  return render_template('forms/edit_artist.html', form=form, artist=artist_query)

#DONE
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  body = {}
  artist = Artist.query.get(artist_id)

  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

#DONE
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = Venue.query.get(venue_id)

  if venue_query:
    form.name.data = venue_query.name
    form.city.data = venue_query.city
    form.state.data = venue_query.state
    form.address.data = venue_query.address
    form.phone.data = venue_query.phone
    form.genres.data = venue_query.genres
    form.facebook_link.data = venue_query.facebook_link
    form.image_link.data = venue_query.image_link
    form.website_link.data = venue_query.website_link
    form.seeking_talent.data = venue_query.seeking_talent
    form.seeking_description.data = venue_query.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_query)

#DONE
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  body = {}
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

#DONE
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead DONE
  # TODO: modify data to be the data object returned from db insertion DONE
  error = False
  body = {}
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website_link']
    seeking_venue = True if 'seeking_venue' in request.form else False
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link,
                  genres=genres, facebook_link=facebook_link, website=website, seeking_venue=seeking_venue,
                  seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead. DONE
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

#DONE
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  query_shows = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in query_shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

#DONE
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead DONE

  error = False
  body = {}
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead. DONE
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
