## Flask-Maple
It's easy to use captcha and bootstrap

### Installation

To install Flask-Maple:

    pip install flask-maple

Or alternatively, you can download the repository and install manually by doing:

    git clone git@github.com:honmaple/flask-maple.git
    cd flask-maple
    python setup.py install
    
### Usage

    from flask_maple import MapleCaptcha,MapleBootstrap
    [...]
    MapleCaptcha(app)
    MapleBootstrap(app)
    
Templates:

    {% extends 'bootstrap/base.html' %}
    {% block main -%}
    <button class="btn btn-primary">asd</button>
    <span class="glyphicon glyphicon-search" aria-hidden="true"></span>
    {% endblock -%}
    
### Config

    AUTHOR_NAME = "This will show you name at html footer"
    CAPTCHA_URL = "The captcha url,default 'captcha'"
    
### Example
   
    python example/run.py
    # http://127.0.0.1:5000

