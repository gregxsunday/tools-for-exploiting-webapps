from flask import Blueprint, request, render_template, Response, flash, g, session, redirect, url_for, \
                  abort, jsonify

import sys
import validators
import json
from os import path, listdir, remove
current_dir = path.dirname(__file__)
sys.path.insert(0, path.join(current_dir, '../../../CORS/AsynchronousCORSScanner/'))

from core.web_run import web_run
from multiprocessing import Process
from datetime import datetime
from app.database.models import Domain, CorsScan, CorsResult, db
from app.common.plot import *

from bokeh.embed import components


mod = Blueprint('cors', __name__)

@mod.route('/cors', methods=['GET'])
def index():
  return (render_template('cors/index.html'))


@mod.route('/cors/run', methods=['POST'])
def run():
    domain = request.form.get('domain')
    log_level = int(request.form.get('log_level'))
    char_mode = int(request.form.get('char_mode'))
    log_path = path.realpath(path.join(current_dir, '../static/logs/'))
    report_path = path.realpath(path.join(current_dir, '../static/cors_reports/'))
    now = datetime.now()
    report_name = now.strftime('%H%M%S_cors')

    if not validators.domain(domain):
        return Response(status=403)
    if log_level < 0 or log_level > 5:
        log_level = 3
    if char_mode < 0 or char_mode > 3:
        char_mode = 0
    try:
        db_domain = Domain.query.filter_by(domain=domain).first()
    except:
        return Response(status=500)
    if db_domain is None:
        db_domain = Domain(domain=domain)
        db.session.add(db_domain)    

    new_scan = CorsScan(scan_status=0, scan_name=report_name, scan_dir=now.strftime('%Y%m%d'), character_mode=char_mode, domain=db_domain)
    Process(target=web_run, args=(domain, log_level, log_path, char_mode, report_path, (report_name + '.json'))).start()
    new_scan.scan_status = 1

    try:
        db.session.commit()
    except:
        return Response(status=500)

    return Response(status=200)


@mod.route('/cors/log', methods=['GET'])
def logs():
    return render_template("cors/logs.html")


@mod.route('/cors/raw/log', methods=['GET'])
def raw_logs():
    log = path.realpath(path.join(current_dir, '../static/logs/cors.log'))
    try:
        with open(log, 'r') as log_file:
            content = log_file.read()
        return f"<pre>{content}<pre>"
    except FileNotFoundError as err:
        return f"There is no logs, are You sure that the scan is running or was running?"
    

@mod.route('/cors/results', methods=['GET'])
def results():
    reports_dir = path.realpath(path.join(current_dir, '../static/cors_reports/'))
    directories = listdir(reports_dir)

    for directory in directories:
        day_reports_dir = path.join(reports_dir, directory)
        reports = listdir(day_reports_dir)
        for report in reports:
            scan = CorsScan.query.filter_by(scan_name=report.split('.')[0]).first()
            if scan is not None and scan.scan_status < 2:
                scan.scan_status = 2
                db.session.commit()
    scans = CorsScan.query.filter(CorsScan.scan_status < 3)
    return render_template('cors/results.html', scans=scans)

# TODO
@mod.route('/cors/results/<name>', methods=['GET'])
def see_result(name):
    scan = CorsScan.query.filter_by(scan_name=name).first()
    report_path = path.realpath(path.join(current_dir, '../static/cors_reports/', scan.scan_dir, scan.scan_name + '.json'))
    creation_time = f"{scan.scan_dir[6:]}/{scan.scan_dir[4:-2]}/{scan.scan_dir[:-4]}, {scan.scan_name[:-9]}:{scan.scan_name[2:-7]}:{scan.scan_name[4:-5]}"
    with open(report_path) as f:
        results = json.loads(f.read())

    plot_data = {
        "Type": [],
        "Amount": []
    }

    for key in results.keys():
        plot_data["Type"].append(key)
        plot_data["Amount"].append(len(results[key]))
    
    plot = create_bar_chart(plot_data, "Chart of the requests results", "Type", "Amount")
    script, div = components(plot)
    return render_template("cors/result.html", div=div, script=script, domain=scan.domain, time=creation_time, x_legend=x_axis_legend, tests_legend=tests_legend, mirrored=results['mirrored_vuln'], credentials=results['credentials_vuln'])


@mod.route('/cors/results/<name>', methods=['POST'])
def delete_result(name):
    scan = CorsScan.query.filter_by(scan_name=name).first_or_404()
    reports_dir = path.realpath(path.join(current_dir, '../static/cors_reports/'))
    report_fullpath = path.join(reports_dir, scan.scan_dir, name + '.json')

    if not report_fullpath.startswith(reports_dir):
        return 'Invalid name', 403

    remove(report_fullpath)
    scan.scan_status = 3
    db.session.commit()
    return redirect('/cors/results', 302)