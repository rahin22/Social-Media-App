from flask import Blueprint, render_template, request, jsonify
from thefuzz import fuzz
from .models import users
import base64

search = Blueprint('search', __name__)

@search.route('/search', methods=['GET', 'POST'])
def search_algorithm():
    if request.method == 'GET':
        query = request.args.get('query', '')
        all_users = users.query.all()

        results = []
        for user in all_users:
            score = fuzz.ratio(query, user.username)
            encoded_pfp = base64.b64encode(user.pfp).decode() if user.pfp else None
            results.append((user.username, score, encoded_pfp, user.bio, user.fullname))
        
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:12]
        dropdown_results = results[:5]

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'results': dropdown_results})
        else:
            return render_template('search_results.html', results=top_results, query=query)

