import concurrent.futures
import requests
import networkx as nx

import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from time import sleep

from utils import get_url

blockchain_info_url = "https://blockchain.info/block-height/"
blockchain_info_url_suffix = "?format=json"
block_file_header = "block_"



def _grab_blocks(begin_block):

    urls = [blockchain_info_url + str(i) + blockchain_info_url_suffix for i in range(begin_block, begin_block+1)]

    with concurrent.futures.ThreadPoolExecutor() as pool:
        received_blocks = list(pool.map(get_url, urls, timeout=30))

    return received_blocks

def _build_graph(blockchain):
    
    graph = nx.MultiDiGraph()
    graph.add_node("Coinbase")

    for block in blockchain:

        current_ntxs = block['blocks'][0]['n_tx']
        current_block = block['blocks'][0]["height"]
        print("Graphing block {}".format(current_block))

        for tx in range(current_ntxs):
            current_transaction = block['blocks'][0]["tx"][tx]
            inputs = block['blocks'][0]["tx"][tx]["inputs"]
            outputs = block['blocks'][0]["tx"][tx]["out"]
            n_of_inputs = int(block['blocks'][0]["tx"][tx]["vin_sz"]) 
            n_of_outputs = int(block['blocks'][0]["tx"][tx]["vout_sz"]) 
            # it is worse because all changes in inputs need to be manually adjusted
            
            is_coinbase = False

            input_vals = {}
            output_vals = {}
            tx_vals_temp = []
            tx_vals = []


            for inputx in range(len(inputs)):
                try:
                    
                    current_input_address = inputs[inputx]["prev_out"]["addr"]
                    current_input_value = inputs[inputx]["prev_out"]["value"]
                    input_vals[current_input_address] = current_input_value
                    graph.add_node(current_input_address)
                
                except:
                    
                    if (n_of_inputs == 1) and (n_of_outputs == 1):
                    
                        #input_vals["Coinbase"] = outputs[0]["value"] #--> which is output value
                        is_coinbase = True
                        graph.add_weighted_edges_from([("Coinbase",outputs[0]["addr"] ,outputs[0]["value"])])
                    
                    else:
                        continue                                     # Add checks for values of difficulty vs reward 
                                                                        # for checking authenticity and to catch simmilar txs that
                                                                        # are not Coinbase
                    
                        # No need to add Coinbase multiple times
                            # already added when creating graph
                # only add inputs here then add outputs and edges together 
                # this seems to be rather inefficient O(n^2)
                # Be careful not to assume seg witness et al are
                # coinbase just because there might not be an input address
                # or an input value

                #Adding input address to graph, doesn't duplicate
                

                if is_coinbase == True: #Then skip output loop because we already added the Tx
                    break

                for out in range(len(outputs)):
                    try:
                        current_output_address = outputs[out]["addr"]
                        current_output_value = outputs[out]["value"]
                    except Exception as e:
                        #import pdb;pdb.set_trace()
                        print(e)

                    if current_output_address in input_vals: # remove from output list and remove the returned 
                                                            # change value from the transaction
                        input_vals[current_output_address] -= current_output_value #Removed change from tx
                        n_of_outputs -= 1 #coinbase txs can still be recorded 
                        continue #don't add to output_vals and later to edges
                    
                    else: #If output is not a change tx, add node then generate edges
                        graph.add_node(current_output_address)
                        output_vals[current_output_address] = current_output_value
                        tx_vals_temp.append([current_input_address,current_output_address, None])

                #if n_of_outputs <= 0: # If it is one of the weird reorganizing txs
                #    continue          # then skip (refer to block 546)
                try:
                    current_input_value = current_input_value/n_of_outputs
                except ZeroDivisionError:
                    #debug_zero_div.append((block_number, tx))
                    print("alarm ____________________________________________ zero division error")
                
                for tx_tuple in tx_vals:
                    tx_tuple[2] = current_input_value
                    tx_tuple = tuple(tx_tuple)
                    tx_vals.append(tx_tuple)

                graph.add_weighted_edges_from(tx_vals)

    return graph

def _plot_graph(G):
    pos = nx.spring_layout(G)

    edge_x = []
    edge_y = []
    print("Number of edges: " + str(len(G.edges())))
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(color='black', width=1),
        hoverinfo='none',
        showlegend=False,
        mode='lines')

    # nodes trace
    node_x = []
    node_y = []
    text = []
    print("Number of nodes: " + str(len(G.nodes())))
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y, text=text,
        mode='markers+text',
        showlegend=False,
        hoverinfo='none',
        marker=dict(
            color='pink',
            size=50,
            line=dict(color='black', width=1)))

    # layout
    layout = dict(plot_bgcolor='white',
                  paper_bgcolor='white',
                  margin=dict(t=10, b=10, l=10, r=10, pad=0),
                  xaxis=dict(linecolor='black',
                             showgrid=False,
                             showticklabels=False,
                             mirror=True),
                  yaxis=dict(linecolor='black',
                             showgrid=False,
                             showticklabels=False,
                             mirror=True))

    # figure
    fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

    return fig
    
def build_block_tx_graph(begin_block):
    begin_block = int(begin_block)
    

    print("First Block: " + str(begin_block))
    
    received_blocks = _grab_blocks(begin_block)
    received_blocks = list(received_blocks)

    tx_graph = _build_graph(received_blocks) 
    g_figure = _plot_graph(tx_graph)
    return g_figure
    ######## Blocks grabbed

    

    
