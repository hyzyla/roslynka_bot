from app import setup

setup.prepare_logging()

app = setup.prepare_app()
db = setup.prepare_db(app)
migration = setup.prepare_migration(app, db)
dispatcher = setup.prepare_dispatcher(app)

from app import handlers

setup.prepare_handlers(dispatcher)

if __name__ == '__main__':
    app.run()
