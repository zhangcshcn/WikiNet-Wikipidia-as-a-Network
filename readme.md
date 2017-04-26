Chen Zhang (cz1389) & Guang Yang (gy552)   

## WikiNet: Wikipedia as a Network  

### Requirements  

- python 2.7  
- django  
- numpy  
- sklearn  
- bs4  
- lxml  

### How to start the web service  
We suggest to run it on  
> ssh linserv1.cims.nyu.edu  

You need to make sure that *python 2.7* is called. So you will have to excute.  

> module load python-2.7  

Otherwise python 2.6 will be the default version to invoke.  
Pick a port number between 10000 and 25000. Then you should cd to the *webdev* directory and excute  

> python manage.py runserver 0.0.0.0: your-port-number/wikiNet/

and the webpage should be available at  

> linserv1.cims.nyu.edu:your-port-number  

#### Notice  
We did most of the computation offline. And the website and its components are all stored in-memory. No database system is used. It could take a REALLY LONG TIME to load all data. So we provide a smaller yet fully functional dataset with the submission. The smaller dataset was crawled starting from /wiki/Apple\_Inc. and contains 456 documents, the maximum depth is 2.  
A project running on a much larger dataset (starting from /wiki/Apple\_Inc. but with maximum depth of 4, containing 6050 documents) is running on  

> linserv1.cims.nyu.edu:13890/wikiNet/  

### How to build WikiNet step by step  

#### Invoke the crawler  
> python hcrawler.py < relative address > < maximum depth >

For example, if your seed will be *https://en.wikipedia.org/wiki/Apple*, then you should put */wiki/Apple* as the relative address.  
The indexed pages will be stored in a sibling directory named *Apple*, named after the index, which will be exported as a sibling file named *Apple.stats*. 
Each line of the *Apple.stats* is organized as  

> "%d %s %s %d",index, relative url, parent's relative url, depth  

##### Known issues:  

- Duplication prevention is not implemented.  
- Some seemingly important pages may be missed.  

#### Extract the main content of the pages and build an directed graph  
> python texify.py < path to the directory where downloaded pages are stored > < name of that diretory >  

The first argument should be a path containing both the diretory of the downloaded pages, and the .stats file.  
The content of the pages downloaded will be extracted and store in a sibling directory *content*.  
And a python pickle file *urlgi.pkl* will be generated, storing the graph.  

#### Generate WikiNet  
> python knowledgeGraph.py < path to the *content* directory and *urlgi.pkl* >  

A *class.pkl* file will be generated under the path.  
In this class encapsulates all the data and motheds that make up WikiNet.  
You should move the *class.pkl* under the django WikiNet diretory.  

##### Known issues: 

There may be some module name inconsistence. In that case you will need to manually load and dump the *class.pkl* file for django view to load the data.  
Just invoke python 2.7 under the WikiNet diretory  

> module load python-2.7  
> python  

to enter the interactive interface. Then  

> import cPickle as pkl  
> from knowledgeGraph import knowledgeGraph  
> with open('class.pkl') as f:  
>   &nbsp;&nbsp; G = pkl.load(f)     # this will take a while  
>  
> with open('class.pkl','w') as f:  
>   &nbsp;&nbsp; pkl.dump(G, f)  # this will also take a while

Then the problems should be solved.  

