import json
import re
from flask import render_template, request, jsonify, url_for, redirect, flash, session
from app import app, db
from models import SearchHistory, ApiStatus
from services.virustotal import VirusTotalService
from services.abuseipdb import AbuseIPDBService
from services.alienvault import AlienVaultService
from services.shodan import ShodanService
from utils import detect_indicator_type, validate_indicator
import logging

# Initialize services
vt_service = VirusTotalService(app.config["VIRUSTOTAL_API_KEY"])
abuse_service = AbuseIPDBService(app.config["ABUSEIPDB_API_KEY"])
otx_service = AlienVaultService(app.config["ALIENVAULT_API_KEY"])
shodan_service = ShodanService(app.config["SHODAN_API_KEY"])

@app.route('/')
def index():
    # Get the API status for each service
    api_statuses = ApiStatus.query.all()
    
    # If no status records exist, initialize them
    if not api_statuses:
        services = [
            {"name": "VirusTotal", "service": vt_service},
            {"name": "AbuseIPDB", "service": abuse_service},
            {"name": "AlienVault OTX", "service": otx_service},
            {"name": "Shodan", "service": shodan_service}
        ]
        
        for service_info in services:
            status = ApiStatus(
                service_name=service_info["name"],
                status="unknown"
            )
            db.session.add(status)
        
        db.session.commit()
        api_statuses = ApiStatus.query.all()
    
    return render_template('index.html', api_statuses=api_statuses)

@app.route('/search', methods=['POST'])
def search():
    indicator = request.form.get('indicator', '').strip()
    
    if not indicator:
        flash('Please enter an indicator to search', 'warning')
        return redirect(url_for('index'))
    
    # Detect indicator type
    indicator_type = detect_indicator_type(indicator)
    
    if not indicator_type:
        flash('Invalid indicator format', 'danger')
        return redirect(url_for('index'))
    
    # Validate indicator format
    if not validate_indicator(indicator, indicator_type):
        flash(f'Invalid format for {indicator_type}', 'danger')
        return redirect(url_for('index'))
    
    # Initialize results dictionary
    results = {
        "virustotal": None,
        "abuseipdb": None,
        "alienvault": None,
        "shodan": None,
        "indicator": indicator,
        "indicator_type": indicator_type
    }
    
    try:
        # Query each service based on indicator type
        if indicator_type in ['ip', 'domain', 'url', 'hash']:
            results["virustotal"] = vt_service.query(indicator, indicator_type)
            update_api_status("VirusTotal", "online")
        
        if indicator_type == 'ip':
            results["abuseipdb"] = abuse_service.check_ip(indicator)
            update_api_status("AbuseIPDB", "online")
            results["shodan"] = shodan_service.lookup_ip(indicator)
            update_api_status("Shodan", "online")
        
        if indicator_type in ['ip', 'domain', 'url', 'hash']:
            results["alienvault"] = otx_service.get_pulse_info(indicator, indicator_type)
            update_api_status("AlienVault OTX", "online")
        
        if indicator_type == 'domain':
            results["shodan"] = shodan_service.lookup_domain(indicator)
            update_api_status("Shodan", "online")
        
    except Exception as e:
        logging.error(f"Error querying services: {str(e)}")
        flash(f"Error during search: {str(e)}", "danger")
    
    # Save search to history
    search_history = SearchHistory(
        indicator=indicator,
        indicator_type=indicator_type,
        results=results
    )
    db.session.add(search_history)
    db.session.commit()
    
    return render_template('results.html', results=results, indicator=indicator, indicator_type=indicator_type)

@app.route('/history')
def history():
    # Get recent searches (most recent first)
    searches = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).limit(50).all()
    return render_template('history.html', searches=searches)

@app.route('/history/<int:search_id>')
def view_search(search_id):
    search = SearchHistory.query.get_or_404(search_id)
    results = search.results
    return render_template('results.html', 
                          results=results, 
                          indicator=search.indicator, 
                          indicator_type=search.indicator_type, 
                          from_history=True)

@app.route('/api/check_api_keys', methods=['GET'])
def check_api_keys():
    services = [
        {"name": "VirusTotal", "service": vt_service, "key": app.config["VIRUSTOTAL_API_KEY"]},
        {"name": "AbuseIPDB", "service": abuse_service, "key": app.config["ABUSEIPDB_API_KEY"]},
        {"name": "AlienVault OTX", "service": otx_service, "key": app.config["ALIENVAULT_API_KEY"]},
        {"name": "Shodan", "service": shodan_service, "key": app.config["SHODAN_API_KEY"]}
    ]
    
    results = {}
    
    for service_info in services:
        name = service_info["name"]
        service = service_info["service"]
        key = service_info["key"]
        
        if not key:
            update_api_status(name, "error", "API key not configured")
            results[name] = {"status": "error", "message": "API key not configured"}
        else:
            try:
                status = service.check_api_key()
                update_api_status(name, "online" if status else "error", None if status else "Invalid API key")
                results[name] = {"status": "online" if status else "error"}
            except Exception as e:
                update_api_status(name, "error", str(e))
                results[name] = {"status": "error", "message": str(e)}
    
    return jsonify(results)

def update_api_status(service_name, status, error_message=None):
    """Update the API status in the database"""
    api_status = ApiStatus.query.filter_by(service_name=service_name).first()
    
    if not api_status:
        api_status = ApiStatus(service_name=service_name)
    
    api_status.status = status
    api_status.error_message = error_message
    
    db.session.add(api_status)
    db.session.commit()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
