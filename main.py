from flask import Flask, jsonify
import urllib.request

app = Flask(__name__)


@app.route('/getTimeStories', methods=['GET'])
def get_time_stories():
    url = "https://time.com/tag/ai/"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    stories = []
    position = 0
    while len(stories) < 6:
        # Looking for the next anchor tag
        a_tag = html.find('<a ', position)
        if a_tag == -1:
            break
        href_start = html.find('href="', a_tag)
        if href_start == -1:
            position = a_tag + 1
            continue
        href_start += len('href="')
        href_end = html.find('"', href_start)
        link = html[href_start:href_end]

        # Finding the span containing the title inside the anchor
        a_close = html.find('>', href_end)
        span_open = html.find('<span>', a_close)
        span_close = html.find('</span>', span_open)
        if span_open == -1 or span_close == -1:
            position = a_close + 1
            continue
        title = html[span_open + len('<span>'):span_close].strip()

        # Moving position past this anchor for the next search
        a_end = html.find('</a>', span_close)
        position = a_end + len('</a>') if a_end != - \
            1 else span_close + len('</span>')

        # Only adding unique, non-empty stories with valid links
        if (link.startswith('http') or link.startswith('/')) and title and not any(s['title'] == title for s in stories):
            if link.startswith('/'):
                link = "https://time.com" + link
            stories.append({
                "title": title,
                "link": link
            })

    return jsonify(stories)


if __name__ == '__main__':
    app.run(debug=True)
