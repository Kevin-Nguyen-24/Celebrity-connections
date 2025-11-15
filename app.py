from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
from collections import deque
from typing import List, Dict, Optional, Set, Tuple
import time
import re

app = Flask(__name__)
CORS(app)

# Predefined list of famous celebrities (global sample)
FAMOUS_CELEBRITIES = [
    # North America
    "Tom Hanks", "Leonardo DiCaprio", "Brad Pitt", "Jennifer Lopez", "Johnny Depp",
    "Meryl Streep", "Denzel Washington", "Robert De Niro", "Scarlett Johansson",
    "Will Smith", "Keanu Reeves", "Angelina Jolie", "Sandra Bullock", "Tom Cruise",
    "Natalie Portman", "Emma Stone", "Ryan Gosling", "Ryan Reynolds",
    "Taylor Swift", "Beyoncé", "Rihanna", "Lady Gaga", "Drake", "Eminem",
    "Jay-Z", "Ariana Grande", "Selena Gomez", "Justin Bieber", "The Weeknd",

    # Europe
    "Adele", "Ed Sheeran", "Dua Lipa", "Harry Styles", "Daniel Craig", "Emma Watson",
    "Benedict Cumberbatch", "Tom Hardy", "Keira Knightley", "Penélope Cruz",
    "Javier Bardem", "Antonio Banderas", "Marion Cotillard", "Monica Bellucci",
    "Gérard Depardieu", "Saoirse Ronan", "Mads Mikkelsen", "Millie Bobby Brown",

    # Latin America
    "Shakira", "Bad Bunny", "Salma Hayek", "Gael García Bernal", "Diego Luna",
    "Pedro Pascal", "Anitta", "Eugenio Derbez", "Karol G", "Maluma",

    # Africa
    "Charlize Theron", "Lupita Nyong'o", "Wizkid", "Burna Boy", "Davido",
    "Black Coffee", "Trevor Noah", "Tiwa Savage",

    # Middle East
    "Gal Gadot", "Mohamed Salah", "Haifa Wehbe",

    # South Asia (Bollywood)
    "Shah Rukh Khan", "Amitabh Bachchan", "Aamir Khan", "Salman Khan",
    "Deepika Padukone", "Priyanka Chopra", "Aishwarya Rai Bachchan", "Alia Bhatt",
    "Ranveer Singh", "Ranbir Kapoor",

    # East Asia
    "Jackie Chan", "Jet Li", "Donnie Yen", "Andy Lau", "Gong Li", "Zhang Ziyi",
    "Fan Bingbing", "Jay Chou", "Ken Watanabe", "Rinko Kikuchi",

    # Korea
    "Song Kang-ho", "Lee Min-ho", "IU (singer)", "Jungkook", "Jennie" ,

    # Oceania
    "Cate Blanchett", "Nicole Kidman", "Hugh Jackman", "Margot Robbie", "Taika Waititi",

    # Global sports icons often linked
    "Cristiano Ronaldo", "Lionel Messi", "Novak Djokovic", "Serena Williams"
]

class WikipediaConnector:
    """Finds connections between celebrities through Wikipedia links"""
    
    def __init__(self):
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        # Set a proper User-Agent per Wikipedia API etiquette and request JSON explicitly
        self.session.headers.update({
            'User-Agent': 'celebrity-connections/1.0 (+https://celebrity-connections.local; contact: support@celebrity-connections.local)',
            'Accept': 'application/json'
        })
        self.cache = {}  # Cache for celebrity info
        self.max_links_per_page = 200  # limit branching factor for faster search
        self.sleep_interval = 0.03     # polite rate limiting per node expansion

    def _get_json(self, params: Dict, retries: int = 2) -> Dict:
        """Make a GET request to Wikipedia API and return JSON with basic resiliency"""
        last_error = None
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(self.base_url, params=params, timeout=15)
                # Retry on transient HTTP errors
                if not resp.ok:
                    last_error = f"HTTP {resp.status_code}"
                    time.sleep(0.3 * (attempt + 1))
                    continue
                # Ensure JSON response
                if 'application/json' not in resp.headers.get('Content-Type', ''):
                    last_error = f"Non-JSON response (Content-Type: {resp.headers.get('Content-Type', '')})"
                    time.sleep(0.3 * (attempt + 1))
                    continue
                return resp.json()
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                time.sleep(0.3 * (attempt + 1))
            except ValueError as e:
                # JSON decode error
                last_error = f"JSON decode error: {e}"
                time.sleep(0.3 * (attempt + 1))
        raise RuntimeError(last_error or 'Unknown error')
    
    def get_celebrity_info(self, title: str) -> Dict:
        """Get detailed information about a celebrity from Wikipedia"""
        if title in self.cache:
            return self.cache[title]
        
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|pageprops|links',
            'exintro': True,
            'explaintext': True,
            'redirects': 1,
            'pllimit': 500,
            'plnamespace': 0,
            'format': 'json'
        }
        
        try:
            data = self._get_json(params)
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return {'title': title, 'entities': [], 'links': [], 'extract': ''}
            page_id = list(pages.keys())[0]
            
            # If page not found, try normalizing via search
            if page_id == '-1':
                suggestions = self.search_celebrity(title)
                if suggestions:
                    normalized = suggestions[0]['title']
                    if normalized != title:
                        return self.get_celebrity_info(normalized)
                return {'title': title, 'entities': [], 'links': [], 'extract': ''}
            
            page = pages[page_id]
            extract = page.get('extract', '') or ''
            links = [link.get('title') for link in page.get('links', []) if 'title' in link]
            # Limit links to reduce branching and improve performance
            if self.max_links_per_page:
                links = links[: self.max_links_per_page]
            
            # Extract entities (studios, companies, etc.) from the text
            entities = self._extract_entities(extract, links)
            
            info = {
                'title': title,
                'extract': extract[:500],  # First 500 chars
                'entities': entities,
                'links': links
            }
            
            self.cache[title] = info
            return info
            
        except Exception as e:
            print(f"Error fetching info for {title}: {e}")
            return {'title': title, 'entities': [], 'links': [], 'extract': ''}
    
    def _extract_entities(self, text: str, links: List[str]) -> List[Dict]:
        """Extract relevant entities like studios, companies, etc."""
        entities = []
        
        # Keywords to identify entity types
        studio_keywords = ['Studio', 'Studios', 'Pictures', 'Films', 'Entertainment', 'Productions']
        company_keywords = ['Company', 'Corporation', 'Inc.', 'LLC', 'Records', 'Music']
        
        for link in links[:100]:  # Check first 100 links
            entity_type = None
            
            if any(keyword in link for keyword in studio_keywords):
                entity_type = 'studio'
            elif any(keyword in link for keyword in company_keywords):
                entity_type = 'company'
            elif link in text[:1000]:  # Entity mentioned in intro
                entity_type = 'related'
            
            if entity_type:
                entities.append({
                    'name': link,
                    'type': entity_type
                })
        
        return entities[:20]  # Limit to 20 entities
    
    def get_page_links(self, title: str, limit: int = 500) -> List[str]:
        """Get all links from a Wikipedia page"""
        info = self.get_celebrity_info(title)
        return info['links']
    
    def search_celebrity(self, query: str) -> List[Dict]:
        """Search for celebrities on Wikipedia"""
        params = {
            'action': 'opensearch',
            'search': query,
            'limit': 10,
            'namespace': 0,
            'format': 'json'
        }
        
        try:
            data = self._get_json(params)
            
            results = []
            if isinstance(data, list) and len(data) >= 4:
                titles = data[1]
                descriptions = data[2]
                urls = data[3]
                
                for i in range(len(titles)):
                    results.append({
                        'title': titles[i],
                        'description': descriptions[i] if i < len(descriptions) else '',
                        'url': urls[i] if i < len(urls) else ''
                    })
            
            return results
        except Exception as e:
            print(f"Error searching for {query}: {e}")
            return []
    
    def find_shortest_path(self, start: str, end: str, max_depth: int = 7, timeout_seconds: float = 10.0) -> Optional[Tuple[List[str], List[Dict]]]:
        """Bidirectional BFS for shortest Wikipedia link path.
        Returns: (path, connection_details) or None
        """
        if start == end:
            return [start], []
        
        start_time = time.time()
        
        # Initialize bidirectional frontiers
        q_start = deque([start])
        q_end = deque([end])
        parent_start: Dict[str, Optional[str]] = {start: None}
        parent_end: Dict[str, Optional[str]] = {end: None}
        depth_start: Dict[str, int] = {start: 1}
        depth_end: Dict[str, int] = {end: 1}
        visited_start: Set[str] = {start}
        visited_end: Set[str] = {end}
        
        def reconstruct(meet: str) -> List[str]:
            # Build path start -> meet
            left = []
            cur = meet
            while cur is not None:
                left.append(cur)
                cur = parent_start[cur]
            left.reverse()  # now start..meet
            # Build path meet -> end (skip meet duplicate)
            right = []
            cur = parent_end[meet]
            while cur is not None:
                right.append(cur)
                cur = parent_end[cur]
            return left + right
        
        while q_start and q_end:
            # Timeout
            if time.time() - start_time > timeout_seconds:
                return None
            
            # Always expand the smaller frontier
            if len(q_start) <= len(q_end):
                for _ in range(len(q_start)):
                    cur = q_start.popleft()
                    cur_depth = depth_start[cur]
                    if cur_depth >= max_depth:
                        continue
                    links = self.get_celebrity_info(cur)['links']
                    for nxt in links:
                        if nxt not in visited_start:
                            visited_start.add(nxt)
                            parent_start[nxt] = cur
                            depth_start[nxt] = cur_depth + 1
                            if nxt in visited_end:
                                path = reconstruct(nxt)
                                details = self._build_connection_details(path, {})
                                return path, details
                            q_start.append(nxt)
                    time.sleep(self.sleep_interval)
            else:
                for _ in range(len(q_end)):
                    cur = q_end.popleft()
                    cur_depth = depth_end[cur]
                    if cur_depth >= max_depth:
                        continue
                    links = self.get_celebrity_info(cur)['links']
                    for nxt in links:
                        if nxt not in visited_end:
                            visited_end.add(nxt)
                            parent_end[nxt] = cur
                            depth_end[nxt] = cur_depth + 1
                            if nxt in visited_start:
                                path = reconstruct(nxt)
                                details = self._build_connection_details(path, {})
                                return path, details
                            q_end.append(nxt)
                    time.sleep(self.sleep_interval)
        
        return None
    
    def _build_connection_details(self, path: List[str], connection_map: Dict) -> List[Dict]:
        """Build detailed information about each connection in the path"""
        details = []
        
        for i in range(len(path)):
            info = self.get_celebrity_info(path[i])
            detail = {
                'title': path[i],
                'extract': info['extract'],
                'entities': info['entities'][:5],  # Top 5 entities
                'step': i
            }
            details.append(detail)
        
        return details

# Initialize connector
connector = WikipediaConnector()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/celebrities', methods=['GET'])
def get_celebrities():
    """Get list of famous celebrities"""
    return jsonify({'celebrities': FAMOUS_CELEBRITIES})

@app.route('/api/celebrity-info/<path:name>', methods=['GET'])
def get_celebrity_details(name):
    """Get detailed information about a specific celebrity"""
    info = connector.get_celebrity_info(name)
    return jsonify(info)

@app.route('/api/search', methods=['GET'])
def search():
    """Search for celebrities"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = connector.search_celebrity(query)
    return jsonify({'results': results})

@app.route('/api/connect', methods=['POST'])
def connect():
    """Find connection between two celebrities"""
    data = request.json
    start = data.get('start')
    end = data.get('end')
    max_depth = int(data.get('max_depth', 7))
    timeout = float(data.get('timeout', 10))
    
    if not start or not end:
        return jsonify({'error': 'Start and end parameters required'}), 400
    
    result = connector.find_shortest_path(start, end, max_depth=max_depth, timeout_seconds=timeout)
    
    if result:
        path, details = result
        return jsonify({
            'success': True,
            'path': path,
            'details': details,
            'length': len(path) - 1
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No connection found within search depth or timed out'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
