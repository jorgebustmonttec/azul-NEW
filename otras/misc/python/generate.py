import os
import random # Added import
import json # Added import

class Album:
    def __init__(self, name, artists, path):
        self.name = name
        self.artists = artists
        self.path = path

path="./albums"
fileNameList=[]
fileNameList = os.listdir(path)

Albums = []

i=0
letter = ''

for fileName in fileNameList:

    
    #print(name)
    if '-' in fileName:
        
        album = fileName.split("-",1)
        album = list(map(lambda x: x.replace('_', " "), album))
        albumName = album[0]
        albumArtists = album[1].split(".")[0].split("-")

        '''
        print(f'n: {i}')
        print(f'album: {albumName}')
        print(f'artist: {albumArtists}')
        print(f'album art: {fileName}')
        print("")
        '''

        albumObj = Album(albumName, albumArtists, fileName)
        Albums.append(albumObj)
    else:
        print(f'album: \'{fileName}\' has incorrect formatting')
    

Albums.sort(key=lambda album: album.name, reverse=False)

for album in Albums:
    if letter != album.name[0]:
        letter = album.name[0]
        print(f'\n\n\n==================== LETTER {letter.upper()} ALBUMS ====================\n\n\n')
    
    print(f'album object n: {i}')
    print(f'album: {album.name}')
    print(f'artist: {album.artists}')
    print(f'album art: {album.path}')
    print("")
    i=i+1


# --- RANDOM SELECTION WITH JSON PERSISTENCE ---
json_file = "albums_selection.json"

if os.path.exists(json_file):
    print(f"Reading existing selection from {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Reconstruct Album objects from JSON data
        Albums = [Album(d['name'], d['artists'], d['path']) for d in data]
else:
    print("Generating new random selection and saving to JSON")
    # --- NEW LOGIC: Randomly select 2-4 albums per letter ---
    albums_by_letter = {}
    for album in Albums:
        first_char = album.name[0].upper()
        if first_char not in albums_by_letter:
            albums_by_letter[first_char] = []
        albums_by_letter[first_char].append(album)

    selected_albums = []
    sorted_letters = sorted(albums_by_letter.keys())

    for char in sorted_letters:
        letter_albums = albums_by_letter[char]
        # Randomly determine limit between 2 and 4
        limit = random.randint(2, 4)
        # Randomly select up to 'limit' albums
        if len(letter_albums) <= limit:
            selection = letter_albums
        else:
            selection = random.sample(letter_albums, limit)
        
        selected_albums.extend(selection)

    # Re-sort the final selection so HTML generation logic (break on letter change) works
    selected_albums.sort(key=lambda album: album.name, reverse=False)

    # Swap the main list to use the filtered one
    Albums = selected_albums
    # --------------------------------------------------------

    # Save to JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        # Convert Album objects to dicts for JSON serialization
        json_data = [{'name': a.name, 'artists': a.artists, 'path': a.path} for a in Albums]
        json.dump(json_data, f, indent=4)


# HTML Generation starts here
output_html = "albums.html"

with open(output_html, "w", encoding="utf-8") as f:
    f.write("<html>\n<body>\n")
    f.write("<table width='100%'>\n")
    
    current_letter = ''
    col_counter = 0
    row_open = False

    for album in Albums:
        # Check first letter for section headers
        first_letter = album.name[0].upper()
        
        if current_letter != first_letter:
            # If a row was open, close it before starting a new letter section
            if row_open:
                f.write("</tr>\n")
                row_open = False
                col_counter = 0

            current_letter = first_letter
            # Write the Section Header
            f.write("<tr>\n")
            f.write(f'  <td colspan="3" class="letra-header"><h2>{current_letter.upper()}{current_letter.lower()}</h2></td>\n')
            f.write("</tr>\n")
        
        # Start a new row if we are at column 0
        if col_counter == 0:
            f.write("<tr>\n")
            row_open = True
        
        # Prepare artists string
        artists_str = ", ".join(album.artists)
        
        # Write the album cell
        f.write("  <th>\n")
        f.write(f'    <img class="album-img" src="albums/{album.path}">\n')
        f.write(f'    <p class="album-name"><b>{album.name}</b></p>\n')
        f.write(f'    <p class="album-artists">{artists_str}</p>\n')
        f.write("  </th>\n")
        
        col_counter += 1
        
        # Close row if we reached 3 columns
        if col_counter == 3:
            f.write("</tr>\n")
            row_open = False
            col_counter = 0

    # Clean up if the last row wasn't closed
    if row_open:
        f.write("</tr>\n")

    f.write("</table>\n")
    f.write("</body>\n</html>")

print(f"Done! Generated {output_html}")

