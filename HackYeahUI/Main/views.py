from django.shortcuts import render,HttpResponse
from django.http import request
from .Article import Article
import ast
import json

def index(request):
    articleUser = Article(input("Please enter a link : "))
    articleUser.run()
    articleUser.findRelated()

    #before upload data make sure the url doesnt exist in the database already
    articleUser.uploadData()
    articleUser.getData()
            

    articles = []

    for result in articleUser.compareTo:
        articles.append(Article(result))

    for article in articles:
        article.run()


    commonWords = []
    commonWordHeadLine = []

    for article in articles:
        for word in article.cleanedList:
            if word in articleUser.cleanedList:
                commonWords.append(word)

    for result in articles:
        for word in article.cleanHeadLine:
            if word in articleUser.cleanHeadLine:
                commonWordHeadLine.append(word)
    for article in articles:
        for word in article.queryWordsArray:
            if word in articleUser.queryWordsArray:
                commonWords.append(word)

    contentPercentage = len(commonWords) *100 / len(articleUser.cleanedList)
    headLinePercentage = len(commonWordHeadLine) *100/len(articleUser.cleanHeadLine)
   

    subjectivityScore = (articleUser.subjectivity) / len(articleUser.sentences)

    websiteScore = 0 

    for i in range(len(articleUser.dbArticles)):
        websiteScore += (articleUser.dbArticles[i]['score'])
        
    articleUser.calculateScore(contentPercentage,headLinePercentage,websiteScore/len(articleUser.dbArticles),subjectivityScore)

    #TO DOS
    #FIND A WAY TO PREVENT DUPLICATES
    #ADD A USER INTERFACE
    #ADD COMMENTS
    #CREATE A READ ME
    return render(request,'Main/index.html',{'websiteScore':websiteScore,
                                             'articleScore':articleUser.score})