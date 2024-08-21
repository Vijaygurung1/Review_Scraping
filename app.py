from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq


app = Flask(__name__)


@app.route('/', methods=['GET'])  # Route to display the home page
@cross_origin()
def home_page():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # Route to show the review comments in a web UI
@cross_origin()
def review():
    if request.method == 'POST':
        try:
            search_string = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + search_string
            u_client = uReq(flipkart_url)
            flipkart_page = u_client.read()

            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[:3]

            if not bigboxes:
                return 'No products found.'

            box = bigboxes[0]
            product_link = f"https://www.flipkart.com{box.div.div.div.a['href']}"
            prod_res = requests.get(product_link)
            prod_res.encoding = 'utf-8'
            prod_html = bs(prod_res.text, "html.parser")

            commentboxes = prod_html.find_all('div', {'class': "RcXBOT"})

            filename = f"{search_string}.csv"
            with open(filename, "w", encoding='utf-8') as fw:
                headers = "Product, Customer Name, Rating, Heading, Comment\n"
                fw.write(headers)
                reviews = []

                for commentbox in commentboxes:
                    try:
                        price = prod_html.find_all("div", {"class": "Nx9bqj CxhGGd"})[0].text
                        name = commentbox.div.div.find_all('p', {'class': '_2NsDsF AwS1CA'})[0].text
                    except (IndexError, AttributeError):
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text
                    except AttributeError:
                        rating = 'No Rating'

                    try:
                        comment_head = commentbox.div.div.div.p.text
                    except AttributeError:
                        comment_head = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        cust_comment = comtag[0].div.text
                    except (IndexError, AttributeError):
                        cust_comment = 'No Comment'

                    my_dict = {
                        "Price": price,
                        "Product": search_string,
                        "Name": name,
                        "Rating": rating,
                        "CommentHead": comment_head,
                        "Comment": cust_comment
                    }
                    reviews.append(my_dict)

            return render_template('results.html', reviews=reviews)

        except Exception as e:
            print(f'The Exception message is: {e}')
            return 'Something went wrong'

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)



