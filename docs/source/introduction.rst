1 Introduction To Flask-Maple
-----------------------------

1.1 Installation
~~~~~~~~~~~~~~~~

To install Flask-Maple:

.. code-block:: python

    pip install flask-maple

Or alternatively, you can download the repository and install manually by doing:

.. code-block:: python

    git clone git@github.com:honmaple/flask-maple.git
    cd flask-maple
    python setup.py install

1.2 Bootstrap
~~~~~~~~~~~~~

You need register csrf before use boostrap

.. code-block:: python

    from flask import Flask
    from flask_maple import MapleBootstrap
    from flask_wtf.csrf import CsrfProtect

     app = Flask(__name__)
     app.config['SECRET_KEY'] = 'hard to guess'
     csrf = CsrfProtect()
     csrf.init_app(app)
     maple = MapleBoostrap()
     maple.init_app(app)
     # or MapleBootstrap(app)

     @app.route('/')
     def index():
         return render_template('index.html')

     if __name__ == '__main__':
         app.run()
         print(app.url_map)

**Templates:**

.. code-block:: html

    {% extends 'maple/base.html' %}
    {% block main -%}
    <button class="btn btn-primary">asd</button>
    <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
    {% endblock -%}

**Config:**

.. code-block:: python

    AUTHOR_NAME = "This will show you name at html footer"

1.3 Captcha
~~~~~~~~~~~

Please install Pillow before use captcha

.. code-block:: python

    pip install pillow

**Usage**:

.. code-block:: python

    from flask_maple import MapleCaptcha
    captcha = MapleCaptcha(app)

Then you can visit `http://127.0.0.1/captcha <http://127.0.0.1/captcha>`_

**Config**:

.. code-block:: python

    CAPTCHA_URL = "The captcha url,default 'captcha'"

1.4 Error
~~~~~~~~~

You don't register app.errorhandler if you use error extension

**Usage**:

.. code-block:: python

    from flask_maple import Error
    error = Error(app)

This extension provides some simple error view

.. code-block:: python

    404
    403
    500

1.5 Login
~~~~~~~~~

It's easy to use login

**Usage**:

.. code-block:: python

    from flask_maple import Auth
    auth = Auth(app, db=db, mail=mail, user_model=User)

Then you can visit `http://127.0.0.1:5000/login <http://127.0.0.1:5000/login>`_
