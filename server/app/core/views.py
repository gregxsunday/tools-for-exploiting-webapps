from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, \
                  abort, jsonify


mod = Blueprint('core', __name__)

@mod.route('/')
def index():
  
  return (render_template('core/index.html'))
