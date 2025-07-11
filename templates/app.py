from flask import Flask, render_template
import json
from datetime import datetime
import os

app = Flask(__name__)

def load_all_news():
    news_data = []
    for filename in os.listdir('.'):
        if filename.startswith('news_') and filename.endswith('.json'):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    news_data.extend(data)
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
    
    # Sort news by date
    news_data.sort(key=lambda x: x['date_scraped'], reverse=True)
    return news_data

@app.route('/')
def index():
    news = load_all_news()
    # Group news by category
    categories = {}
    for item in news:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    return render_template('index.html', categories=categories)

@app.route('/trigger_scrape', methods=['POST'])
def trigger_scrape():
    try:
        import news_scraper
        success = news_scraper.main()
        if success:
            flash('News scraping completed successfully!', 'success')
        else:
            flash('News scraping completed but no items were found.', 'warning')
    except Exception as e:
        flash(f'Error during scraping: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/update_sources', methods=['POST'])
def update_sources():
    try:
        config = load_config()
        data = request.get_json()
        
        if not data or 'category' not in data or 'sources' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400
            
        if not isinstance(data['sources'], list):
            return jsonify({'status': 'error', 'message': 'Sources must be a list'}), 400
            
        config['news_sources'][data['category']] = data['sources']
        save_config(config)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/update_theme', methods=['POST'])
def update_theme():
    try:
        config = load_config()
        data = request.get_json()
        
        if not data or 'theme' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400
            
        config['theme'] = data['theme']
        save_config(config)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)