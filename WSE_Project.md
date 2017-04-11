Chen Zhang (cz1389) & Guang Yang (gy552)   

### Goals  

Fuzzy query on Wikipedia page. 

### Motivations  

Wikipedia pages are so specified that it is immune to fuzzy queries.  
For example, when we search on wikipedia for "apple", there is no chance that you get any clue about "banana", although both of them are fruit.  
From time to time, people are interested in the extension of a keyword. In the case of "apple", the searcher may want to find out about information about general fruits, or even about many other objects and concepts relating to apples.  
We would like answer a query with a cluster, or clusters of relating wikipedia pages. 

### Features  

- We will build an indexer and a huristic crawler for wikipedia pages. 
- We will cluster the pages hirarchically based on not only content but also topological features of wikipedia as a graph. 
- We will match one or more clusters of related pages with one query. 
- We may investigate the sementic path between to wikipedia pages. 


