from flask import Blueprint, request, render_template, Response, flash, g, session, redirect, url_for, \
                  abort, jsonify

import sys
import validators
from os import path, listdir, remove
current_dir = path.dirname(__file__)
sys.path.insert(0, path.join(current_dir,'../../../SSRF/'))

from payload_generator.web_run import web_run
from multiprocessing import Process
from app.database.models import SSRFPayload, db
from datetime import datetime


mod = Blueprint('ssrf_payload', __name__)

@mod.route('/payloads/ssrf_payloads', methods=['GET'])
def index():
    return (render_template('ssrf_payloads/index.html'))


@mod.route('/payloads/create_payloads', methods=['POST'])
def create():
    target_domain = request.form.get('target_domain')
    forgery_domain = request.form.get('forgery_domain')
    log_path = path.realpath(path.join(current_dir, '../static/logs/'))
    list_path = path.realpath(path.join(current_dir, '../static/payloads/'))
    now = datetime.now()
    list_name = now.strftime('%H%M%S_payloads')

    if not validators.domain(target_domain) and not validators.ip_address.ipv4(target_domain):
        return Response(status=403)
    if not validators.domain(forgery_domain) and not validators.ip_address.ipv4(forgery_domain):
        return Response(status=403)
    
    new_list = SSRFPayload(payload_name=list_name, payload_dir=now.strftime('%Y%m%d'), target_domain=target_domain, forgery_domain=forgery_domain)
    Process(target=web_run, args=(target_domain, forgery_domain, list_path, (list_name + '.txt'), log_path)).start()

    try:
        db.session.add(new_list)
        db.session.commit()
    except:
        return Response(status=500)

    return Response(status=200)


@mod.route('/payloads/lists', methods=['GET'])
def lists():
    payloads = SSRFPayload.query.all()
    return render_template('ssrf_payloads/lists.html', payloads=payloads)


@mod.route('/payloads/lists/<name>', methods=['GET'])
def payload(name):
    payload = SSRFPayload.query.filter_by(payload_name=name).first()
    payload_path = path.realpath(path.join(current_dir, '../static/payloads/', payload.payload_dir, payload.payload_name + '.txt'))

    try:
        with open(payload_path, 'r') as payload_file:
            content = payload_file.read()
        return render_template('ssrf_payloads/list.html', content=content)
    except FileNotFoundError as err:
        return render_template('ssrf_payloads/list.html', content='There is no list with this name')


@mod.route('/payloads/lists/<name>', methods=['POST'])
def delete_payload(name):
    payload = SSRFPayload.query.filter_by(payload_name=name).first_or_404()
    payloads_dir = path.realpath(path.join(current_dir, '../static/payloads/'))
    payload_fullpath = path.join(payloads_dir, payload.payload_dir, name + '.txt')

    if not payload_fullpath.startswith(payloads_dir):
        return 'Invalid name', 403

    remove(payload_fullpath)
    try:
        db.session.delete(payload)
        db.session.commit()
    except Exception as err:
        return Response(status=500)
    return redirect('/payloads/lists', 302)