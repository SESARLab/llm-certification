import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges
G.add_node("start:start")
G.add_node("check:capabilities")
G.add_node("check:read-only-filesystem")
G.add_node("check:non-root-user")
G.add_node("evaluation:base")
G.add_node("if:seccomp")
G.add_node("check:seccomp")
G.add_node("evaluation:final")

G.add_edge("start:start", "check:capabilities")
G.add_edge("start:start", "check:read-only-filesystem")
G.add_edge("start:start", "check:non-root-user")
G.add_edge("check:capabilities", "evaluation:base")
G.add_edge("check:read-only-filesystem", "evaluation:base")
G.add_edge("check:non-root-user", "evaluation:base")
G.add_edge("evaluation:base", "if:seccomp")
G.add_edge("if:seccomp", "check:seccomp")
G.add_edge("if:seccomp", "evaluation:final")
G.add_edge("check:seccomp", "evaluation:final")

# Print adjacency
print(G.adj)

def draw_graph(graph):
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.show()

def evaluate_graph(graph, start,check_attributes):
    visited = set()
    queue = deque([start])

    current_eval_block=[]
    current_ifs=[]
    eval_res={}

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            if "check" in node:
                current_eval_block.append({"node":node,"result":check_attributes.get(node)})

            if "if" in node:
                current_ifs.append(node)

            if "evaluation" in node:
                for check in current_eval_block:
                    if eval_res.get(node) is None:
                        eval_res[node]={}
                        eval_res[node]["checks"]={}
                        eval_res[node]["result"]=True
                    
                    if check["result"]==False and check["node"].split(":")[1] not in [if_node.split(":")[1] for if_node in current_ifs]:
                        print(f"Evaluation block {node} failed on check failure on {check['node']}")
                        eval_res[node]["checks"][check["node"]]=False
                        eval_res[node]["result"]=False
                    elif check["result"]==False and check["node"].split(":")[1] in [if_node.split(":")[1] for if_node in current_ifs]:
                        print(f"Evaluation block {node} skipped on check failure on {check['node']}")
                        eval_res[node]["checks"][check["node"]]=False
                        eval_res[node]["result"]=False
                    elif check["result"]==None and check["node"].split(":")[1] in [if_node.split(":")[1] for if_node in current_ifs]:
                        print(f"Evaluation block {node} skipped on check failure on {check['node']}")
                        eval_res[node]["checks"][check["node"]]=None
                    else:
                        print(f"Evaluation block {node} passed on check {check['node']}")
                        eval_res[node]["checks"][check["node"]]=True
                print(f"Evaluation block {node} result: {eval_res[node]['result']}")
                current_eval_block=[]  # Reset for next evaluation block
                current_eval_block.append({"node":node,"result":eval_res[node]["result"]})  # Start new block with current evaluation node
                current_ifs=[]  # Reset if conditions

            #print(node, graph.nodes[node])  # Node and its attributes
            # Add neighbors to the queue (children in DAG)
            queue.extend(graph.successors(node))  # Only follow directed edges down
    
    return eval_res