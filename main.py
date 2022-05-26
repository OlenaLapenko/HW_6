from flask import Flask, jsonify, request, render_template
from http import HTTPStatus
from database_handler import execute_query
from utils import format_data
app = Flask(__name__, static_url_path='/static')


@app.errorhandler(HTTPStatus.UNPROCESSABLE_ENTITY)
@app.errorhandler(HTTPStatus.BAD_REQUEST)
def error_handling(error):
    headers = error.data.get("headers", None)
    messages = error.data.get("messages", ["Invalid request."])

    if headers:
        return jsonify(
            {
                'errors': messages
            },
            error.code,
            headers
        )
    else:
        return jsonify(
            {
                'errors': messages
            },
            error.code,
        )


@app.route("/")
def order_price():
    country_arg = request.args.get('country')
    if country_arg:
        try:
            query = f'SELECT SUM (UnitPrice * Quantity) ' \
                    f'FROM invoice_items JOIN invoices ' \
                    f'ON invoice_items.InvoiceId = invoices.InvoiceId ' \
                    f'WHERE invoices.BillingCountry = \'{country_arg}\''
            records = execute_query(query=query)[0]
            return render_template('result.html', country=country_arg, total=round(records[0],3))
        except Exception as e:
            return render_template('result.html', country='None', total=0)
    else:
        query = 'SELECT SUM (UnitPrice * Quantity) FROM invoice_items'
        records = execute_query(query=query)[0]
        return render_template('result.html', country='All', total=round(records[0],3))


@app.route("/track")
def get_all_info_about_track():
    # join all possible tables and show all possible info about all tracks
    track_lasting_query = f'SELECT SUM(Milliseconds) FROM tracks'
    track_query = f'SELECT tracks.Name, tracks.Composer, artists.Name, albums.Title, playlists.Name, genres.Name, ' \
                  f'media_types.Name, tracks.Milliseconds,tracks.Bytes, tracks.UnitPrice ' \
                  f'FROM tracks ' \
                  f'JOIN albums ON tracks.AlbumId = albums.AlbumId ' \
                  f'JOIN artists ON artists.ArtistId = albums.ArtistId ' \
                  f'JOIN genres ON genres.GenreId = tracks.GenreId ' \
                  f'JOIN media_types ON media_types.MediaTypeId = tracks.MediaTypeId ' \
                  f'JOIN playlist_track ON playlist_track.TrackId = tracks.TrackId ' \
                  f'JOIN playlists ON playlists.PlaylistId = playlist_track.PlaylistId'
    track_lasting = execute_query(query=track_lasting_query)[0]
    track_data = execute_query(query=track_query)
    return render_template('track.html', data=track_data, lasting=str(track_lasting[0]))



app.run(debug=True, port=5000)
