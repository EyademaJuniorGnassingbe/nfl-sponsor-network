import csv
import random

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
g = nx.Graph()

with open("nfl_brand_deals.csv","r") as in_file:
        data_set = csv.DictReader(in_file)#makes a dictionary(each row in the google sheet is its own little dictionary) where the column names/headers are the keys and the content in the row are the values
        for team_and_sponsor_info in data_set: #gives a line consisting of the team name,brand name,category,subcategory,and years active
            
            team_name = team_and_sponsor_info["TEAM"] #the specific name of one team
            brand_name = team_and_sponsor_info["BRANDS"] #the specific name of one brand
            
         #(pertaining to the code below) I'm building a bipartite graph so I need 2 different nodes
            g.add_node(team_name,type = "team") #first node,team and the type is team(need to distinguish between team and brand)
            g.add_node(brand_name,type = "brand")#second node, brand and the type is brand
            
            g.add_edge(team_name,brand_name) #edge between team name and brand name
            
        #pertaining to the code above,(the graph is done I have everything I need)
        #data sheet already tells me if they have a connection or not
        #so no need to create a nested loop to 
        
        print("Nodes:", len(g.nodes))
        top_k = 50
        c_degree = nx.degree_centrality(g)#calculates degree centrality (number of connections in normalized form)
     
        brand_degree = {} #new empty dictionary that will only hold brand nodes and their degree centrality scores
        for node in c_degree: #loops through every node (team and brand mixed) in the original c_degree dictionary
            if g.nodes[node]["type"] == "brand": #checks this node's type attribute, only keep going if it's a brand
                brand_degree[node] = c_degree[node] #copies this brand's centrality score into the new filtered dictionary
         
        percentile_list = []
        
        early_stage = {} #new empty dictionary for brands with degree 1 to 3, holds brand name and its raw degree
        expansion = {} #new empty dictionary for brands with degree 4 to 31, holds brand name and its raw degree
        for node in sorted(brand_degree, key=brand_degree.get, reverse=True):#[:top_k]: #sorts degree by their key instead of
            #alphabetically or numerically which is the default and makes it count highest to lowest.
                
            
                        
                    
                #print(node, g.nodes[node], brand_degree[node], g.degree[node]) #prints edge name,
                    #type,normalized count of connections, regular number of connectios
                  
                            
                percentile_list.append((g.degree[node]))
                
        percentile = np.percentile(percentile_list,[90,95,99])
        print(percentile)
        degree_counts =pd.Series(percentile_list).value_counts().sort_index()
        print(degree_counts)
        
   

        for node in brand_degree: #loops through every brand (teams were already filtered out of brand_degree)
            d = g.degree[node] #raw number of teams this brand sponsors

            if d <= 3: #3 teams or fewer means early stage
                early_stage[node] = d #saves the brand and its degree in the early stage bucket
            elif d <= 31: #4 to 31 teams means expansion,32s not included 
                expansion[node] = d #saves the brand and its degree in the expansion bucket

        print("Early-stage brands:", len(early_stage)) #should be 8030
        print("Expansion brands:", len(expansion)) #should be 634
        
        all_teams = set() #empty set that will hold the name of every team node
        for node in g.nodes: #loops through every node in the graph (teams and brands mixed)
            if g.nodes[node]["type"] == "team": #only keeps the nodes tagged as teams
                all_teams.add(node) #adds this team to the set

        print("Teams:", len(all_teams)) #should be 32

        missing_teams = {} #they is brand names, values are a list of teams that brand is NOT connected to
        for brand in expansion: #loops through every brand in the expansion bucket
            connected_teams = set(g.neighbors(brand)) #the teams this brand already sponsors 
            missing_teams[brand] = sorted(all_teams - connected_teams) #teams in the full set but not in this brand's set, sorted alphabetically

        #quick look at a few brands to check the results make sense
        for brand in list(expansion)[:5]: #takes the first 5 brands in the expansion bucket
            print(brand, "| teams:", expansion[brand], "| missing:", len(missing_teams[brand]), missing_teams[brand])
        
        top_leads = sorted(expansion, key=lambda b: (-expansion[b], b))[:10] #sorting by most teams first and if two brands have the same number of teams, then they're sorted alphabetically"

        print("Top 10 expansion leads (ranked by degree)")
        for brand in top_leads: #loops through the 10 highest degree brands in the expansion bucket
            print(brand, "| teams:", expansion[brand], "| missing:", len(missing_teams[brand]), "|", ", ".join(missing_teams[brand])) #brand, how many teams it sponsors, how many it's missing, and which ones        
                    
        
            
        
        plt.bar(degree_counts.index, degree_counts.values) #one bar per degree value
        plt.yscale("log") #log scale so the big bar doesn't hide the small ones
        plt.xlabel("Number of teams a brand sponsors")
        plt.ylabel("Number of brands (log scale)")
        plt.title("NFL sponsors by number of teams")
        plt.savefig("degree_distribution.png") #saves the image 
        plt.show()
        
        top_table = pd.DataFrame({ #builds a small table from the top 10 list
        "Brand": top_leads,
        "Teams": [expansion[b] for b in top_leads],
        "Missing": [len(missing_teams[b]) for b in top_leads],
        "Missing teams": [", ".join(missing_teams[b]) for b in top_leads],
    })
        print(top_table.to_string(index=False)) 
