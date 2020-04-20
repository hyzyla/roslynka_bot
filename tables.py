from app import db
import models


class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'

    id = models.Integer(primary_key=True)
    username = models.Text(nullable=True)
    first_name = models.Text(nullable=True)
    last_name = models.Text(nullable=True)
    language_code = models.Text(nullable=True)

    user_id = models.ForeignKey('users.id', unique=True)
    user = db.relationship('User')

    date_created = models.DateCreated()


class User(db.Model):
    __tablename__ = 'users'

    id = models.UUID()

    home_id = models.ForeignKey('homes.id', nullable=True)
    home = db.relationship('Home')

    date_created = models.DateCreated()


class Home(db.Model):
    __tablename__ = 'homes'

    id = models.UUID()
    date_created = models.DateCreated()
    plants = db.relationship('Plant')


class Plant(db.Model):
    __tablename__ = 'plants'

    id = models.UUID()
    name = models.Text()
    watering_interval = models.Interval()
    photo_id = models.Text(nullable=True)

    home_id = models.ForeignKey('homes.id')
    home = db.relationship('Home')

    date_created = models.DateCreated()


class PlantWatering(db.Model):
    __tablename__ = 'plant_watering'

    id = models.UUID()
    date = models.DateCreated()
    plant_id = models.ForeignKey('plants.id')
    user_id = models.ForeignKey('users.id')
