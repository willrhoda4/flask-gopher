





from flask                    import Flask, jsonify
from scripts.wrangle_imdb     import fetch_imdb_ids
from handlers.flicks_handler  import get_flicks
from handlers.posters_handler import process_new_credits
from scripts.update_credits   import update_credits_on_node

import os
import cloudinary.uploader




# Your Node API URL and token, dynamically fetched
node_api_url = os.getenv('NODE_API_URL', 'http://localhost:5000')
github_token = os.getenv('GITHUB_TOKEN')


def update_database():

    try:
    
        # step 1: Fetch IMDb IDs
        team_ids, db_credits = fetch_imdb_ids(f"{node_api_url}/wrangleImdbIds", github_token)
        if not team_ids:
            return jsonify({"error": "Failed to fetch IMDb IDs"}), 500

        # step 2: Fetch stunt credits for the team
        total_credits, unique_films = get_flicks(team_ids)

        # step 3: Process posters for new credits
        new_credits_info = process_new_credits(db_credits, unique_films)

        # step 4: Send updated credits to Node API
        update_credits_on_node(new_credits_info, node_api_url, github_token)

        return jsonify({
            "status": "success",
            "total_credits": total_credits,
            "unique_films": unique_films,
            "new_posters": new_credits_info
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

