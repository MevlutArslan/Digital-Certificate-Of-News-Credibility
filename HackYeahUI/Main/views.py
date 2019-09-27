from django.shortcuts import render,HttpResponse
from django.http import request
from .Article import Article
import ast
import json
from firebase_admin import credentials
import firebase_admin

cred = credentials.Certificate('./Main/sconc-4473d-firebase-adminsdk-xqwlf-32bb728a96.json')
firebase_admin.initialize_app(cred)

def index(request):
    websiteScore = None
    articleScore = None
    url = request.POST.get('url')
    if url is not None:
        articleUser = Article(url)
        url = articleUser.link
        articleUser.initFirebase()
        articleUser.run()
        articleUser.findRelated()
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

        urls = []
        error = ''

        for i in range(len(articleUser.dbArticles)):
            urls.append(articleUser.dbArticles[i]['link'])

        #before upload data make sure the url doesnt exist in the database already
        if url not in urls:
            articleUser.uploadData()
        else:
            error = 'We already have this article in our database here are the results'
        
        #TO DOS
        #ADD COMMENTS
        #CREATE A READ ME
        articleScore = articleUser.score 

    return render(request,'Main/index.html',{'url':url,
                                             'websiteScore':websiteScore,
                                             'articleScore':articleScore})
