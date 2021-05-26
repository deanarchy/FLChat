import os
import sys
import click

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Conversation, Message

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = create_app(os.getenv('FLASK_ENV') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, User=User, Conversation=Conversation,
        Message=Message
    )


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run test w/ coverage')
def test(coverage):
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Summary: ')
        COV.report()
        cov_dir = os.path.join(BASE_DIR, 'tmp/coverage')
        COV.html_report(directory=cov_dir)
        print(f'HTML version: file://{cov_dir}/index.html')
        COV.erase()