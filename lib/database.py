from orator import DatabaseManager, Model
from orator.orm import has_many_through

config = {
  'postgres': {
    'driver': 'postgres',
    'host': 'localhost',
    'database': 'tw',
    'user': 'tw',
    'password': 'dontatme',
    'prefix': '',
    'log_queries': True
  }
}

db = DatabaseManager(config)
Model.set_connection_resolver(db)

class ListUser(Model):
  pass

class User(Model):
  pass

class List(Model):
  @has_many_through(ListUser, 'list_id', 'id')
  def users(self):
    return User

