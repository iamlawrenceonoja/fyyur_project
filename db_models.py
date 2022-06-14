from app import db

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Show ID: {self.id}, {self.artist_id} city={self.venue_id} state={self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(400))
    website_link = db.Column(db.String(400))
    shows = db.relationship('Show', backref ='venue', lazy=True)

    def __repr__(self):
      return f'<Venue ID: {self.id}, {self.name} city={self.city} state={self.state}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate DONE

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String, nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    website = db.Column(db.String(400))
    seeking_description = db.Column(db.String(400))
    shows = db.relationship('Show', backref ='artist', lazy=True)

    def __repr__(self):
      return f'<Artist ID: id={self.id}, name={self.name} city={self.city} state={self.state}>'


db.create_all()
