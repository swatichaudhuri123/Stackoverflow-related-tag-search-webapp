import requests
import networkx as nx
import pandas as pd
from flask import Flask,render_template,url_for,request,redirect
app= Flask(__name__)
base_urls = []


def get_urls(x):
    urls = base_urls.append(url)
    return urls


for page in range(1, 101):
    url = 'https://api.stackexchange.com/2.2/questions?page=' + str(
        page) + '&pagesize=100&order=desc&sort=activity&site=stackoverflow'
    get_urls(url)
for b in base_urls:
  r = requests.get(b)
  r.json()


df=pd.DataFrame.from_dict(r.json()["items"])
tag_list=df['tags'].to_list()
g=nx.Graph()
def weighted_graph(tag_list):
  for tags in tag_list:
    if len(tags)==1:
      if tags[0] not in list(g.nodes()):
        g.add_node(tags[0])
  else:
    while len(tags)>1:
      tag=tags.pop(0)
      if tag not in list(g.nodes()):
        g.add_node(tag)
      for temp_tag in tags:
        if (tag,temp_tag) not in g.edges([tag]):
          g.add_edge(tag,temp_tag,weight=1)
        else:
          g[tag][temp_tag]['weight']+=1
      if tags[0] not in list(g.nodes()):
        g.add_node(tags[0])
serialized_graph = nx.readwrite.json_graph.node_link_data(g)

#nodes is a list of all the nodes in the graph
nodes = serialized_graph['nodes']

#edges is a list of all the edges in the graph
edges  = serialized_graph['links']

#storing the nodes in a text file
with open('nodes.txt', 'w') as outfile:
    json.dump(edges, outfile)

#storing the edges in a text file
with open('edges.txt', 'w') as outfile:
    json.dump(edges, outfile)


def related_tags(edges_list, tag):
    '''
    function to get related tags
    edges_list : contains all the edges from the graph
    tag : given tag
    '''
    max_related_tags = 10
    tag_weight = []
    for edge in edges_list:
        if edge['source'] == tag:
            temp = []
            temp.append(edge['target'])
            temp.append(edge['weight'])
            tag_weight.append(temp)
        elif edge['target'] == tag:
            temp = []
            temp.append(edge['source'])
            temp.append(edge['weight'])
            tag_weight.append(temp)    
    sorted_weight_tag = sorted(tag_weight , key = lambda x:x[1] , reverse = True) #sorting the weights in decreasing order
    top_related_tags_list = [x[0] for x in sorted_weight_tag] #getting the realted tags based on the weights
    if len(top_related_tags_list) < max_related_tags:
        return top_related_tags_list
    else:
        return top_related_tags_list[:max_related_tags]

@app.route('/', methods=['GET', 'POST'])
def main():
	if flask.request.method == 'GET':
		return(flask.render_template('index.html'))
	if flask.request.method == 'POST':
		tag_given = flask.request.form['Tag']
		with open('nodes.txt') as json_file:
			node_dict = json.load(json_file)
		node_list = []
		for node in node_dict:
			node_list.append(node['id'])
		if tag_given not in node_list:
			return flask.render_template('index.html',
                                     original_input={'Given tag':tag_given },
                                     result=['Error : Given tag not present'],
                                     )

		with open('edges.txt') as json_file:
			edge_list = json.load(json_file)

		top_related_tags_list =  related_tags(edge_list,tag_given)
		return flask.render_template('index.html',
                                     original_input={'Given tag':tag_given },
                                     result=top_related_tags_list,
                                     )
if __name__ == '__main__':
    app.run(debug = True)
