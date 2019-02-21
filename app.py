# first we have to instantiate Flask (our framework)
from flask import Flask

# this lets us render html templates
from flask import render_template

# create the app
app = Flask(__name__)

# settings
FB_GRAPH_API_ACCESS_TOKEN = '720834224743084%7C20163018cebd534e691754afde74b307'
MASHAPE_API_KEY = 'JWOtin6BxKmshCtTRBK8tBggcaQyp1KyZ1BjsniNdApx4wDToL'

# app routes serve specific functionality based on the URL being accessec
@app.route('/')
def index():
    # this is the user-facing web app
    return render_template('index.html')

@app.route('/search_fake_news')
def fake_news_script():
    # this is the server-side script which responds to requests from the web app

    # receive & parse requests (also make fancy responses)
    from flask import request, jsonify

    # make external HTTP requests & JSON parsing
    import requests, json

    # allows us to download files to the user's computer
    from flask import Response

    if request.method == 'GET':
        query = request.args.get('query')
        download = request.args.get('download')
        sort_by = 'relevant' # hardcoded for now
        if (query):
            # set request variables
            hoaxy_url = 'https://api-hoaxy.p.mashape.com/articles'
            request_headers = {'x-mashape-key': MASHAPE_API_KEY}

            # make the request
            hoaxy = requests.get(hoaxy_url, params={'query': query}, headers=request_headers).content

            # make the CSV file
            # format:
            # ..........................................
            # ....title,source,number_of_tweets,number_of_shares (shares is not yet supported by Hoaxy API)
            # ...."Hillary Clinton actually the descendant of lizards","evil-lizards.net/hillaryisoneofus", 257

            # the first line of our CSV file (which determines its structure)
            csv_content = 'title,source,date,site_type,number_of_tweets,number_of_fb_shares\n'

            # converting into a Python dictionary and extracting the articles array
            hoaxyJson = json.loads(hoaxy)
            articles_array = hoaxyJson['articles']

            # we will iterate through the articles array and grab values for the keys we want
            for article in articles_array:
                name = article.get('title')
                name = name.replace('"','')
                name = '"'+name+'"'

                source = '"'+article.get('canonical_url')+'"'
                date = str(article.get('publish_date'))
                site_type = str(article.get('site_type'))
                tweets = str(article.get('number_of_tweets'))


                # we also want to get FB shares, but this isn't returned by the Hoaxy API. This forces us to make a call directly to the FB Graph API with an APP
                graph_url = "https://graph.facebook.com/v2.8/"
                graph = requests.get(graph_url, params={'id': article.get('canonical_url'), 'access_token': FB_GRAPH_API_ACCESS_TOKEN}).content
                graphJson = json.loads(graph)
                fb_shares = str(graphJson['share']['share_count'])

                # concatenating all these variables into a line of our CSV
                csv_content += name+','+source+','+date+','+site_type+','+tweets+','+fb_shares+'\n'

            # remove last new line (\n)
            csv_content = csv_content.rstrip()

            # we will spit out a formatted CSV fragment and raw JSON response
            if (download):
                # download the file (not an AJAX request)
                return Response(csv_content, mimetype='text/csv')
            else:
                # return an object for javascript manipulation
                return jsonify(csv=csv_content, json=hoaxy)
        else:
            return 'missing_parameters'
    else:
        return 'invalid_request'
