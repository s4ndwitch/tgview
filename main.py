#!/bin/python

from flask import jsonify
import webbrowser
from flask import Flask, render_template
from sqlite3 import connect
from threading import Thread
from configparser import ConfigParser


def parse_config() -> (str, int):
    config = ConfigParser()
    if len(config.read('config.ini')) == 0:
        raise(FileNotFoundError('No \'config.ini\' file found in here'))
    try:
        return config['CONFIG']['address'], int(config['CONFIG']['port'])
    except KeyError:
        raise(KeyError('No \'address\' or \'port\' found or no \'[CONFIG]\' in \'config.ini\''))
    except ValueError:
        raise(ValueError('\'port\' is not int'))


def init_server(ADDRESS: str, PORT: int) -> None:
    app = Flask(__name__)

    @app.route("/getChannels")
    def get_channels():
        return jsonify(connect("db.sqlite").cursor().execute("SELECT title FROM channel;").fetchall())

    @app.route("/")
    def index():
        return render_template("index.html")

    app.run(host=ADDRESS, port=PORT)


if __name__ == "__main__":
    ADDRESS, PORT = parse_config()
    thread = Thread(target=init_server, args=(ADDRESS, PORT))
    thread.start()
    webbrowser.open("http://%s:%i/" % (ADDRESS, PORT))
    thread.join()

