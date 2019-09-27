from bs4 import BeautifulSoup
import urllib.request
import nltk
from textblob import TextBlob
import re
import string
import datetime
from nltk import tokenize
from newsapi import NewsApiClient
import sys
import spacy
nlp = spacy.load('en')
import pke
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random


class Article:
    
    #Constructor
    def __init__(self,url):
        self.link = url
        self.websites = {"BBC News" : {"id" : "bbc-news", "url" : "bbc.co.uk", "headlineTag" : "story-body__h1", "headlineTag2" : None, "contentTag" : "story-body__inner", "contentTag2" : "p", "isAttribute" : True, "dateTag" : "div", "dateTag2" : "data-datetime", "dateFormat" : "%d %B %Y"},
                        "ABC News" : {"id" : "abc-news", "url" : "abcnews.go.com", "headlineTag" : "article-header", "headlineTag2" : "h1", "contentTag" : "article-copy", "contentTag2" : "p", "isAttribute" : False , "dateTag" : "timestamp", "dateTag2" : None, "dateFormat" : "%b %d, %Y, %I:%M %p ET"},
                        "The Washington Post" : {"id" : "the-washington-post", "url" : "washingtonpost.com", "headlineTag" : "topper-headline", "headlineTag2" : "h1", "contentTag" : "article-body", "contentTag2" : "p", "isAttribute" : True, "dateTag" : "span", "dateTag2" : "content", "dateFormat" : "%Y-%m-%dT%I:%M-500"},
                        "AP News" : {"id" : "associated-press", "url" : "apnews.com", "headlineTag" : "headline", "headlineTag2" : "h1", "contentTag" : "Article", "contentTag2" : "p", "isAttribute" : True, "dateTag" : "span", "dateTag2" : "data-source", "dateFormat" : "%Y-%m-%dT%H:%M:%SZ"}
                        }
        self.id = ''.join(random.choice(string.ascii_letters) for i in range(6))
        self.score = 0
    
    # Getting content, headline, and publish date of the news.
    def webScrap(self):
        self.content = ""
        self.headline = ""
        self.publishDate = ""

        self.currentWebsite = ''
        for i in self.websites:
            if self.websites[i]["url"] in self.link:
                self.currentWebsite = self.websites[i]
                break

        source = urllib.request.urlopen(self.link)
        soup = BeautifulSoup(source, "lxml")

        #gets all strings in header tag of the target article
        for i in soup.findAll(class_ = self.currentWebsite["headlineTag"]):
            if self.currentWebsite["headlineTag2"] == None:
                self.headline += i.text
            else:
                for x in soup.findAll(self.currentWebsite["headlineTag2"]):
                    self.headline += x.text
        #gets all strings in content tag of the target article (AKA the paraghraphs)
        for i in soup.findAll(class_ = self.currentWebsite["contentTag"]):
            if self.currentWebsite["contentTag2"] == None:
                self.content += i.text
            else:
                for x in soup.findAll(self.currentWebsite["contentTag2"]):
                    self.content += x.text

        #gets the date data and format data
        if self.currentWebsite["isAttribute"] == True:
            for i in soup.findAll(self.currentWebsite["dateTag"]):
                if i.has_attr(self.currentWebsite["dateTag2"]):
                    self.publishDate = i[self.currentWebsite["dateTag2"]]
                    break
        else:
            for i in soup.findAll(class_ = self.currentWebsite["dateTag"]):
                if self.currentWebsite["dateTag2"] == None:
                    self.publishDate = i.text
                    break
                else:
                    for x in i.findAll(class_ = self.currentWebsite["dateTag"]):
                        self.publishDate = x.text
                        break

        def formatDate(date):
            if chr(151) in date:
                date = date.split(chr(151) + " ")
                return date[1]
            else:
                return date

        if self.currentWebsite["id"] == "abc-news":
            self.publishDate = formatDate(self.publishDate)

        self.publishDate = datetime.datetime.strptime(self.publishDate, self.currentWebsite["dateFormat"]).date()



    def cleanText(self):
        self.webScrap()
        #article text content
        text = self.content.lower()
        #article header content
        head = self.headline.lower()
        stopWords = ["ve","''",'”','’',',','.','-', '--', 'a', 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually',
                'after', 'afterwards', 'again', 'against', 'ain’t', 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 
                'amongst', 'amoungst', 'amount', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate',
                'appropriate', 'are', 'aren’t', 'around', 'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'a’s', 'back', 'be', 'became', 'because', 'become',
                'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beneath', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'bill', 'both',
                'bottom', 'brief', 'but', 'by', 'call', 'came', 'can', 'cannot', 'cant', 'can’t', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes',
                'con', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', 'couldnt', 'couldn’t', 'course',
                'currently', 'c’mon', 'c’s', 'de', 'definitely', 'describe', 'described', 'despite', 'detail', 'did', 'didn’t', 'different', 'do', 'does', 'doesn’t', 'doing', 'done', 'don’t', 'down',
                'downwards', 'due', 'during', 'each', 'edu', 'eg', 'either', 'else', 'elsewhere', 'empty', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'excepting', 'far', 'few', 'fify', 'fill', 'find', 'fire', 'first', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'found', 'from', 'front', 'full', 'further', 'furthermore', 'get', 'gets', 'getting', 'give', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', 'hadn’t', 'happens', 'hardly', 'has', 'hasnt', 'hasn’t', 'have', 'haven’t', 'having', 'he', 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'here’s', 'hers', 'herself', 'he’s', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'hundred', 'i', 'ie', 'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'inside', 'insofar', 'instead', 'interest', 'into', 'inward', 'is', 'isn’t', 'it', 'its', 'itself', 'it’d', 'it’ll', 'it’s', 'i’d', 'i’ll', 'i’m', 'i’ve', 'just', 'keep', 'keeps', 'kept', 'know', 'known', 'knows', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'let’s', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'made', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'part', 'particular', 'particularly', 'past', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'put', 'que', 'quite', 'qv', 'rather', 'rd', 're', 'really', 'reasonably', 'regard', 'regarding', 'regardless', 'regards', 'relatively', 'respect', 'respectively', 'right', 's', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'several', 'shall', 'she', 'should', 'shouldn’t', 'show', 'side', 'since', 'sincere', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'spite', 'still', 'sub', 'such',
                'sup', 'sure', 'system', 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'that’s', 'the', 'their', 'theirs', 'them', 'themselves', 
                'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'theres', 'thereupon', 'there’s', 'these', 'they', 'they’d', 'they’ll', 'they’re', 'they’ve', 
                'think', 'this', 'thorough', 'thoroughly', 'those', 'though', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'told', 'too', 'took', 'top', 'toward', 'towards',
                'tried', 'tries', 'truly', 'try', 'trying', 'twice', 't’s', 'un', 'under', 'underneath', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use',
                'used', 'useful', 'uses', 'using', 'usually', 'value', 'various', 'very', 'via', 'viz', 'vs', 'want', 'wants', 'was', 'wasn’t', 'way', 'we', 'welcome', 'well', 'went', 'were', 
                'weren’t', 'we’d', 'we’ll', 'we’re', 'we’ve', 'what', 'whatever', 'what’s', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 
                'where’s', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'who’s', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', 'wonder', 
                'won’t', 'would', 'wouldn’t', 'yes', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'you’d', 'you’ll', 'you’re', 'you’ve', 'zero']

        self.words = []
        self.sentences = []
        self.headerWords = []

        self.words = tokenize.word_tokenize(text,language='english')
        self.sentences = tokenize.sent_tokenize(text,language='english')
        self.headerWords = tokenize.word_tokenize(head,language='english')
        self.cleanedList = [x for x in self.words if not x in stopWords]
        newList = []
        for x in self.cleanedList:
            newList.append(''.join(c for c in x if c not in string.punctuation))
        self.cleanedList = list(set(newList))

        self.cleanHeadLine = [x for x in self.headerWords if not x in stopWords]



    def opinionCheck(self):
        scores = []
        textBlob = ''

        for sentence in self.sentences:
            textBlob = TextBlob(sentence)
            scores.append(textBlob.sentiment.subjectivity)
        
        self.subjectivity = 0
        for score in scores:
            self.subjectivity = self.subjectivity + score
        
        if self.subjectivity >= (self.subjectivity / 2):
            return True
        else:
            return False

        
        
    def findRelated(self):
        sourcesToSearch = ''

        newsapi = NewsApiClient('c3ef595ba6414146b09332ae73cdf0eb')

        for x in range(len(list(self.websites.values()))):
            if self.currentWebsite["id"] != list(self.websites.values())[x]["id"]:
                 sourcesToSearch += list(self.websites.values())[x]["id"] + ", "

        #gets all the related news articles based on the data we feed it.
        result = (newsapi.get_everything(q = self.queryWordsStr,
                                    sources = sourcesToSearch,
                                    from_param = str(self.publishDate),
                                    to = str(self.publishDate + datetime.timedelta(days=7)),
                                    language='en'))
        
        #puts all the related articles into an array to use for comparison
        self.compareTo = []
        if result["totalResults"] != 0:
            for x in range(len(result["articles"][0]["source"]) - 1):
                self.compareTo.append(result["articles"][x]["url"])     
        else:
            print("NO RESULT FOUND")


    #uses PKE library to get keywords to find related news articles
    def findQueryWords(self,k = 2):

        extractor = pke.unsupervised.TopicRank()

        text_file = open("Output.txt", "w",encoding='utf-8')
        
        text_file.write(self.content)

        text_file.close()

        extractor.load_document(input = 'Output.txt', language='en')

        extractor.candidate_selection()

        extractor.candidate_weighting()

        #gets a list of keywords based on how many keywords we want for efficiency purposes during the demo we fixed it to 2
        self.queryWords = extractor.get_n_best(n = k)
        self.queryWordsStr = ''
        self.queryWordsArray = []

        for i in range(len(self.queryWords)):
            self.queryWordsStr += self.queryWords[i][0] + " "
            self.queryWordsArray.append(self.queryWords[i][0])
    
    def calculateScore(self,contentPercentage,headLinePercentage,subjectivityScore,websiteScore):
        contentPercentage = (contentPercentage * 40) / 100
        headLinePercentage = (headLinePercentage * 20) / 100
        websiteScore = (websiteScore * 30) / 100
        subjectivityScoreVal = 0 
        #re-do the point assigning for subjectivity score
        if subjectivityScore <= 0.05:
            subjectivityScoreVal = 100
        if subjectivityScore <= 0.10:
            subjectivityScoreVal = 90
        if subjectivityScore <= 0.15:
            subjectivityScoreVal = 80
        if subjectivityScore <= 0.20:
            subjectivityScoreVal = 70
        if subjectivityScore <= 0.25:
            subjectivityScoreVal = 60
        if subjectivityScore <= 0.30:
            subjectivityScoreVal = 50
        if subjectivityScore <= 0.35:
            subjectivityScoreVal = 40  
        if subjectivityScore <= 0.40:
            subjectivityScoreVal = 30
        if subjectivityScore <= 0.45:
            subjectivityScoreVal = 20
        if subjectivityScore <= 0.50:
            subjectivityScoreVal = 10

        self.score = contentPercentage + headLinePercentage + websiteScore + subjectivityScoreVal

    def initFirebase(self):
        self.db=firestore.client()

    #uploads data to firestore database
    def uploadData(self):
        doc_ref = self.db.collection(u''+self.currentWebsite['id']).document(u''+self.id)
        doc_ref.set({
            u'link':self.link,
            u'score':self.score
        })
    #retrieves data from firestore database
    def getData(self):
        self.docs = self.db.collection(u''+self.currentWebsite['id']).stream()
        self.dbArticles = []
        for doc in self.docs:
            self.dbArticles.append(doc.to_dict())

   

    #runs all the necessary methods in order
    def run(self):
        self.cleanText()
        self.opinionCheck()
        self.findQueryWords()
        
