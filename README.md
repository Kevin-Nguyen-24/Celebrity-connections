# Celebrity Connections

A beautiful web application that discovers how famous celebrities are connected through Wikipedia links. Enter two celebrity names and watch as the app finds the shortest path between them through Wikipedia articles!

## Features

- **Smart Search**: Auto-complete search powered by Wikipedia API
- **Shortest Path Algorithm**: Uses Breadth-First Search (BFS) to find the shortest connection
- **Beautiful UI**: Modern, responsive design with gradient colors and smooth animations
- **Visual Path Display**: Clear visualization of the connection path with color-coded nodes
- **Real-time Search**: Instant celebrity suggestions as you type

## How It Works

The application uses Wikipedia's API to:
1. Search for celebrities based on your input
2. Retrieve all links from each celebrity's Wikipedia page
3. Use BFS algorithm to find the shortest path between two celebrities
4. Display the connection chain in a beautiful, easy-to-understand format

For example, you might find that "Tom Hanks" connects to "Kevin Bacon" through movies they've both appeared in, or through mutual collaborators!

## Requirements

- Python 3.7+
- Flask
- Requests library

## Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd C:\Users\kevin\Projects\celebrity-connections
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Search for celebrities**:
   - Type a celebrity name in the first input field
   - Select from the autocomplete suggestions
   - Do the same for the second celebrity
   - Click "Find Connection"

4. **View the results**:
   - The app will display the shortest path between the two celebrities
   - Each step shows how they're connected through Wikipedia links

## Project Structure

```
celebrity-connections/
├── app.py                 # Flask backend with Wikipedia API integration
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── style.css         # Beautiful styling with gradients
│   └── script.js         # Frontend JavaScript logic
└── README.md             # This file
```

## API Endpoints

### GET `/api/search?q={query}`
Search for celebrities on Wikipedia.

**Response:**
```json
{
  "results": [
    {
      "title": "Celebrity Name",
      "description": "Brief description",
      "url": "Wikipedia URL"
    }
  ]
}
```

### POST `/api/connect`
Find the shortest path between two celebrities.

**Request Body:**
```json
{
  "start": "Celebrity 1",
  "end": "Celebrity 2"
}
```

**Response:**
```json
{
  "success": true,
  "path": ["Celebrity 1", "Connection 1", "...", "Celebrity 2"],
  "length": 3
}
```

## Examples to Try

- Tom Hanks → Kevin Bacon
- Albert Einstein → Taylor Swift
- Barack Obama → Leonardo DiCaprio
- Elon Musk → Marie Curie
- Beyoncé → Isaac Newton

## Algorithm Details

The app uses **Breadth-First Search (BFS)** to find the shortest path:

1. Start with the first celebrity's Wikipedia page
2. Retrieve all links from that page
3. Check if any link matches the target celebrity
4. If not, add all links to a queue and repeat
5. Continue until the target is found or max depth is reached
6. Return the shortest path discovered

The search is limited to a maximum depth of 4 to ensure reasonable response times.

## Technologies Used

- **Backend**: Python, Flask, Flask-CORS
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API**: Wikipedia API
- **Algorithm**: Breadth-First Search (BFS)

## Notes

- The search is limited to a depth of 4 links to keep response times reasonable
- Rate limiting is implemented to respect Wikipedia's API guidelines
- Not all celebrity pairs will have a connection within the search depth
- The app only searches through Wikipedia article links (not external links)

## Future Improvements

- Add caching to speed up repeated searches
- Implement bi-directional BFS for faster results
- Add more visualization options (graph view)
- Support for multiple languages
- Historical search tracking
- Share results functionality

Enjoy discovering celebrity connections!
