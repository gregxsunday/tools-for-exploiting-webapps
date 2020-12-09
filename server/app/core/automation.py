from flask import Blueprint, request, render_template, Response, flash, g, session, redirect, url_for, \
                  abort, jsonify

import sys
import validators


mod = Blueprint('automation', __name__)

@mod.route('/configure', methods=['GET'])
def index():
    return (render_template('/automation/index.html'))
