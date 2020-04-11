from app import db
import models


class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'

    id = models.UUID()
    user_id = models.ForeignKey('users.id', unique=True)
    date_created = models.DateCreated()


class User(db.Model):
    __tablename__ = 'users'

    id = models.UUID()
    date_created = models.DateCreated()


class Home(db.Model):
    __tablename__ = 'homes'

    id = models.UUID()
    date_created = models.DateCreated()


class Plant(db.Model):
    __tablename__ = 'plants'

    id = models.UUID()
    name = models.Text()
    watering_interval = models.Interval()

    date_created = models.DateCreated()


class HomePlant(db.Model):
    __tablename__ = 'home_plants'

    id = models.UUID()
    home_id = models.ForeignKey('homes.id')
    plant_id = models.ForeignKey('plants.id')
    date_created = models.DateCreated()


class HomeUser(db.Model):
    __tablename__ = 'home_users'

    id = models.UUID()
    home_id = models.ForeignKey('homes.id')
    plant_id = models.ForeignKey('users.id')
    date_created = models.DateCreated()