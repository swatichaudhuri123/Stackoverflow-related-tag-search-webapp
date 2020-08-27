import requests
import networkx as nx
import pandas as pd
from flask import Flask,render_template,url_for,request,redirect
app= Flask(__name__)
base_urls = []


def get_urls(url):
    urls = base_urls.append(url)
    return urls






class Graph:
    Tag_G = None

    def __init__(self):
        self.Tag_G = nx.Graph()

    def createGraph(self, stack_exchange_tags):
        for tag in stack_exchange_tags:
            prev = []
            for item in tag:
                if item not in self.Tag_G:
                    self.Tag_G.add_node(item)
                if(len(prev) != 0):
                    for node in prev:
                        if(self.Tag_G.has_edge(item, node)):
                            wt = self.Tag_G[item][node]["weight"]
                            self.Tag_G[item][node]["weight"] = wt+1
                        else:
                            self.Tag_G.add_edge(item, node, weight=1)
                prev.append(item)

    def generateEdgeList(self):
        print("Edge List:")
        for ed in nx.generate_edgelist(self.Tag_G):
            print(ed)

    def findNeighborsOfaTag(self, tag):
        try:
            neighbors_list = list(self.Tag_G.neighbors(tag))
            edge_with_weights = []
            for neighbor in neighbors_list:
                wt = self.Tag_G.get_edge_data(tag, neighbor)
                edge_with_weights.append((neighbor, wt["weight"]))
            edge_with_weights = tuple(
                sorted(edge_with_weights, key=lambda x: x[1], reverse=True))
            associated_tags = self.generateAssociatedTags(
                tag, edge_with_weights)
            return associated_tags
        except nx.NetworkXError:
            return []

    def generateAssociatedTags(self, tag, edge_with_weights):
        associatedTags = []
        for edge in edge_with_weights:
            associatedTags.append(edge[0])
        return associatedTags[:5]

@app.route('/', methods=['GET', 'POST'])
def index():
    for page in range(1, 101):
        url = 'https://api.stackexchange.com/2.2/questions?page=' + str(
            page) + '&pagesize=100&order=desc&sort=activity&site=stackoverflow'
        get_urls(url)
    for b in base_urls:
        r = requests.get(b)
        r.json()
    df = pd.DataFrame.from_dict(r.json()["items"])
    tag_list = df['tags'].to_list()
    graph = Graph()
    graph.createGraph(tag_list)
    if (request.method == 'GET'):
        return render_template('index.html', show_tag=False)
    else:
        query = request.form.to_dict()
        associated_tags = graph.findNeighborsOfaTag(str(query['query']).lower())
        return redirect(url_for('tag_results', tags=associated_tags))

@app.route('/tag_result')
def tag_results():
    tags = request.args.getlist("tags")
    return render_template('index.html', tags=tags, show_tag=True)

if __name__ == "__main__":
    app.run(debug=True)

