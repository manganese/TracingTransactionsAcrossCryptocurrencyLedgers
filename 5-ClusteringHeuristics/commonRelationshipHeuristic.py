__author__ = 'haaroon'
'''
Common Relationship Heuristic

Output: If two users send to the same user then they are common users of a service
Inout: If one user sends to two different addresses

Users are addresses, Each distinct user has a distinct address.
'''
import pandas as pd
import pickle
import networkx as nx
import pprint

def addToGraph(currencypkl, g):
    '''
    Adds the input and output addresses from data from the currency file into the graph,
    :param currencypkl: currency.pkl file which contains a dictionary of key,values. Keys are txids, value are transaction details
    :param g: directed networkx graph
    :return: directed networkx graph, with new nodes and edges
    '''
    skip = 0
    for txid in currencypkl:
        if len(currencypkl[txid])!=1:
            skip+=1
            continue
        for tx in currencypkl[txid]:
            if tx['status'] != 'complete':
                skip += 1
                continue
            if 'Phase1' not in tx:
                skip+=1
                continue
            from_addrs = list(tx['Phase1']['Addresses'])
            from_type = tx['incomingType']
            to_type = tx['outgoingType']
            to_addr = str(tx['withdraw'])+'-'+str(to_type)
            if to_addr not in g:
                g.add_node(to_addr)#, type=to_type)
            # should be a dict but u never know
            divisor = len(from_addrs)
            for f in from_addrs:
                from_addr = str(f)+'-'+str(from_type)
                if from_addr not in g:
                    g.add_node(from_addr, type=from_type)
                # check if edge exists, if so append count, else make a new one
                if g.has_edge(from_addr, to_addr):
                    g.edges[from_addr, to_addr]['weight'] += 1
                else:
                    g.add_edge(from_addr, to_addr, weight=1, curIn=from_type, curOut=to_type)
    print(str(skip)+' txs skipped cause empty or no Phase1')
    print(str(len(currencypkl)-skip)+' txs processed')
    return g

def getEdgeData(n,g):
    '''
    Gets information about a specific nodes edges in the graph, both its inputs and outputs.
    Returns this as a count of currencies that were used as input and output, only returns counts.
    :param n: node to question
    :param g: networkx directed graph
    :return: curIn data and curOut data,
    '''
    alledges = g.in_edges(n)
    curIn = {}
    curOut = {}
    for edge in alledges:
        data = g.get_edge_data(edge[0], edge[1])
        if data['curIn'] in curIn:
            curIn[data['curIn']]+=1
        else:
            curIn[data['curIn']] = 1
    alledges = g.out_edges(n)
    for edge in alledges:
        data = g.get_edge_data(edge[0], edge[1])
        if data['curOut'] in curOut:
            curOut[data['curOut']]+=1
        else:
            curOut[data['curOut']] = 1
    return curIn, curOut


def getExpandedEdgeData(n,g):
    '''
    Gets information about a specific nodes edges in the graph, both its inputs and outputs.
    Returns this as a dict of currencies that were used as input and output, with counts and addresses.
    :param n: node to question
    :param g: networkx directed graph
    :return: curIn data and curOut data,
    '''
    allinedges = g.in_edges(n)
    alloutedges = g.out_edges(n)
    curIn = {}
    curOut = {}
    for edge in allinedges:
        data = g.get_edge_data(edge[0], edge[1])
        if data['curIn'] in curIn:
            curIn[data['curIn']]['count']+=1
            curIn[data['curIn']]['addrs'].append(edge[0])
        else:
            curIn[data['curIn']]={'count':1,'addrs':[edge[0]]}

    for edge in alloutedges:
        data = g.get_edge_data(edge[0], edge[1])
        if data['curOut'] in curOut:
            curOut[data['curOut']]['count']+=1
            curOut[data['curOut']]['addrs'].append(edge[1])
        else:
            curOut[data['curOut']]={'count':1,'addrs':[edge[1]]}
    return curIn, curOut



def getType(g):
    '''
    returns the type of currency the node is
    :param g: networkx directed graph
    :return: dict of types
    '''
    types = {}
    for n in g.nodes():
        node = g.node[n]
        addr_type = node.get('type')['type']
        if addr_type in types:
            types[addr_type]+=1
        else:
            types[addr_type]=1
    return types


def main():
    print("Reading pkls")
    zcash = pickle.load(open('zec.pkl','rb'))
    dash = pickle.load(open('dash.pkl','rb'))
    etc = pickle.load(open('etc.pkl','rb'))
    eth = pickle.load(open('eth.pkl','rb'))
    bch = pickle.load(open('bch.pkl','rb'))
    doge = pickle.load(open('doge.pkl','rb'))
    ltc = pickle.load(open('ltc.pkl','rb'))
    btc = pickle.load(open('btc.pkl','rb'))
    print('putting them into a graph with users')
    g = nx.DiGraph()
    g = addToGraph(zcash, g)
    g = addToGraph(dash, g)
    g = addToGraph(bch, g)
    g = addToGraph(doge, g)
    g = addToGraph(ltc, g)
    g = addToGraph(etc, g)
    g = addToGraph(eth, g)
    g = addToGraph(btc, g)
    print('freeing ram')
    del zcash
    del etc
    del dash
    del doge
    del bch
    del ltc
    del eth
    del btc
    print('here are the results')
    print('# of nodes : ' + str(g.number_of_nodes()))
    print('# of edges : ' + str(g.number_of_edges()))
    print('highest out degree - users that basically use shape shift a lot')
    print('top ten users of shapeshift')
    # top ten users of shapeshift
    topOutDegree = sorted(g.out_degree(), key=lambda kv: kv[1], reverse=True)
    pprint.pprint(topOutDegree[:10])
    print('******')
    print('Output heuristic : if two nodes send to the same, then they are common users of a service-'
          'group these users, list the node, node stats, find top ten')
    print('highest in-degree - Addresses that received lots of coins from a shift - perhaps a service?')
    # TODO TOP TEN NODES THAT HAVE LOTS OF IN-DEGREE, in-degree and their users?
    topInDegree = sorted(g.in_degree(), key=lambda kv: kv[1], reverse=True)
    topins = []
    for pair in topInDegree:
        if pair[1] == 0:
            continue
        else:
            topins.append(pair)
    topInDegree=topins
    topInDegree = sorted(topInDegree, key=lambda kv: kv[1], reverse=True)

    for n in topInDegree[:10]:
        curInData, curOutData = getEdgeData(n,g)
        print(str(n) + ' '+str(g.node[n[0]])+' '+'curInData :' + str(sorted(curInData.items(), key=lambda kv: kv[1], reverse=True)))
        #print('curOutData :' + str(curOutData))

    '''
    highest in-degree - Addresses that received lots of coins from a shift - perhaps a service? e.g. 
('3NJ6GKoqQ5WwrhWctpic9jQctmRC5xGUJH--BTC', 12928) {'type': 'BTC'} curInData :[('ETH', 4553), ('LTC', 3687), ('DASH', 2461), ('DOGE', 1010), ('BCH', 886), ('ETC', 331)]
 '''
    print('******')
    print('Input heuristic : If one user sends to two different addresses - then cluster these two addresses they send'
          ' to')
    print('Generating input graph')
    inputGraph = nx.Graph()
    for n in g.node:
        outEdges = g.out_edges(n)
        if len(outEdges) == 0:
            continue
        prevNode = None
        for outEdge in outEdges:
            type = g.node[outEdge[1]]
            if outEdge[1] not in inputGraph:
                inputGraph.add_node(outEdge[1], type=type)
            if prevNode is None:
                prevNode = outEdge[1]
                continue
            inputGraph.add_edge(prevNode, outEdge[1])
            prevNode = outEdge[1]
    print('Generating clusters')
    print('Number of clusters found : ' + str(nx.number_connected_components(inputGraph)))
    inputComponents = list(nx.connected_component_subgraphs(inputGraph))
    numnodes = [(subg, subg.number_of_nodes()) for subg in inputComponents]
    topinputComponentsNodes = sorted(numnodes, key=lambda kv: kv[1], reverse=True)
    print('top components found')
    pprint.pprint(topinputComponentsNodes[:10])
    for ingr in topinputComponentsNodes[:10]:
        types = getType(ingr[0])
        print('Size :' +str(ingr[1])+' '+'Types :' + str(types))
    ''' e.g. 
    Number of clusters found : 651450
    # Size :39761 Types :{'BTC': 14466, 'BCH': 2710, 'DOGE': 3778, 'LTC': 5715, 'RDD': 589, 'DGB': 1357, 'ETH': 3370, 'NEO': 58, 'SALT': 100, 'XRP': 1442, 'DCR': 104, 'DASH': 725, 'VTC': 584, 'XMR': 738, 'BLK': 377, 'NXT': 125, 'KMD': 174, 'ZEC': 422, 'ETC': 608, 'WAVES': 115, 'RLC': 24, 'GUP': 11, 'XEM': 156, 'GNT': 217, 'CLAM': 48, 'BAT': 73, 'POT': 215, 'SC': 203, 'EOS': 321, 'ZRX': 101, 'REP': 33, 'SNT': 33, 'MONA': 26, 'BTG': 65, 'WINGS': 8, 'OMG': 159, 'FCT': 12, 'DNT': 27, 'SWT': 3, 'FUN': 68, 'MTL': 6, 'STORJ': 27, 'QTUM': 55, 'EDG': 28, 'CVC': 36, 'ANT': 28, 'VRC': 28, 'LBC': 43, 'GAME': 68, 'BNT': 25, 'NMR': 14, 'TRST': 11, 'RCN': 5, 'ZIL': 5, 'USDT': 1, 'SNGLS': 5, 'BNB': 6, 'START': 2, 'GNO': 4, 'MANA': 1, 'TUSD': 2, 'POLY': 1}
    # combined edges proper count without duplicate nodes
    '''
    mycoins_in = {'ZEC':set(),
               'DASH':set(),
               'BTC':set(),
               'BCH':set(),
               'LTC':set(),
               'ETC':set(),
               'ETH':set(),
               'DOGE':set(),
    }
    mycoins_out = {'ZEC':set(),
               'DASH':set(),
               'BTC':set(),
               'BCH':set(),
               'LTC':set(),
               'ETC':set(),
               'ETH':set(),
               'DOGE':set(),
    }

    c=0
    for n in g.nodes():
        c+=1
        if c % 100000 == 0:
            print(str(c)+'/2995250')
        typex = g.node[n]['type']
        if typex not in mycoins:
            continue
        outedges = g.out_edges(n)
        inedges = g.in_edges(n)
        #for e in outedges:
        #    mycoins_out[typex].add(e[1])
        for e in inedges:
            mycoins_in[typex].add(e[0])
    print('in')
    for k in mycoins_in:
        print(k+' '+str(len(mycoins_in[k])))
    print('out')
    for k in mycoins_out:
        print(k+' '+str(len(mycoins_out[k])))


if __name__ == '__main__':
    '''
    Runs the task
    '''
    main()


