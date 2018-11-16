from flask import Flask
from flask import send_from_directory

from flask_mail import Mail

from config import config
from .logging import init_logging

# should be comment
#from .admin import init_admin

from .models import db

mail = Mail()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app);

    init_logging(app)
    db.init_app(app)
    # should be comment
    #init_admin(app)
    mail.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/<string:shopcode>')
    #app.register_blueprint(api_blueprint, url_prefix='/api')

    from .payment import payment as payment_blueprint
    app.register_blueprint(payment_blueprint, url_prefix='/pay/<string:shopcode>')

    from .weixin import weixin as weixin_blueprint
    app.register_blueprint(weixin_blueprint, url_prefix='/weixin')

    # just for develop
    @app.route('/media/<path:filename>', methods=['GET'])
    def media(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=False)

    return app
