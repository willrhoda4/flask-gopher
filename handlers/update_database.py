






import sys
import os

# dynamically add the project root to sys.path
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

if project_root not in sys.path: sys.path.append(project_root)




from flask                    import Flask, jsonify
from scripts.wrangle_imdb     import fetch_imdb_ids
from handlers.flicks_handler  import get_flicks
from handlers.posters_handler import process_new_credits
from scripts.update_credits   import update_credits_on_node

import cloudinary.uploader




# Your Node API URL and token, dynamically fetched
node_api_url = os.getenv('NODE_API_URL', 'http://localhost:5000')
github_token = os.getenv('API_TOKEN')


def update_database():
    try:
        print("Fetching IMDb IDs...")
        team_ids, db_credits = fetch_imdb_ids(f"{node_api_url}/wrangleImdbIds", github_token)
        if not team_ids:
            print("Failed to fetch IMDb IDs")
            return {"error": "Failed to fetch IMDb IDs"}, 500
        
        print(f"Fetched team IDs: {team_ids}")

        # Fetch stunt credits for the team
        print("Fetching stunt credits...")
        total_credits, unique_films = get_flicks(team_ids)

        # Process posters for new credits
        print("Processing new credits...")
        new_credits_info = process_new_credits(db_credits, unique_films)

        # Send updated credits to Node API
        print("Sending updated credits to Node API...")
        update_credits_on_node(new_credits_info, node_api_url, github_token)

        return {
            "status": "success",
            "total_credits": total_credits,
            "unique_films": unique_films,
            "new_posters": new_credits_info
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}, 500


