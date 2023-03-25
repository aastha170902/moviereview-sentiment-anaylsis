# -*- coding: utf-8 -*-
"""moviereviewanalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PzhIn8lzczP0E1JBzIqzr7iy4ohBeUNa
"""

# utilities
import re
import numpy as np
import pandas as pd
# plotting
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# nltk
from nltk.stem import WordNetLemmatizer
# sklearn
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv('IMDB Dataset.csv',engine='python',error_bad_lines=False)

df.head()

df.columns

print('length of data is', len(df))

df. shape

df.info()

sns.countplot(x ='sentiment', data = df)
 
# Show the plot
plt.show()

for i in range(5):
  print("Review number ",[i],"\n")
  print(df['review'].iloc[i], "\n")
  print("Sentiment: ", df['sentiment'].iloc[i], "\n\n")

# let's define function to count number of words in each review

def count_words(text):
  words = text.split()
  num_words = len(words)
  return num_words

df['word count'] = df['review'].apply(count_words)
df.head()

# let's see the number of words for each sentiment
fig, ax = plt.subplots(1,2, figsize=(14,6))
sns.histplot(df[df['sentiment'] == 'positive']['word count'], ax=ax[0], color='blue')
ax[0].set_title('Distrbution of positive reviews')
sns.histplot(df[df['sentiment'] == 'negative']['word count'], ax=ax[1], color='red')
ax[1].set_title('Distrbution of negative reviews')

"""# **Processing**"""

import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))

df.head()

# define function to clean the reviews
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

def preprocess(text):
  soup = BeautifulSoup(text, "html.parser") #Removing the html strips
  text = soup.get_text()
  text = re.sub(r"https\S+|www\S+|http\S+", '', text, flags = re.MULTILINE)
  text = re.sub(r'[A-Za-z0-9]*@[A-Za-z]*\.?[A-Za-z0-9]*', "", text, flags = re.MULTILINE)  #Removing emails 
  text = re.sub('\[[^]]*\]', '', text)  #Removing the square brackets
  text = re.sub(r'[^a-zA-z0-9\s]', '', text)  #Removing special character and keep only words and numbers
  text_tokens = word_tokenize(text)
  filtered_text = [w for w in text_tokens if not w in stop_words]  #Removing stop words
  new_text = " ".join(filtered_text)
  ps = nltk.porter.PorterStemmer()  #Stemming the text
  new_text = ' '.join([ps.stem(word) for word in new_text.split()])
  return new_text

# check it
preprocess("hello we will study natural language processing via this notebook")

# let's see duplicated reviews if any before preprocessing
duplicated_count = df.duplicated().sum()
print("Number of duplicate entries: ", duplicated_count)

# let's apply it on reviews
df.review = df['review'].apply(preprocess)

# check duplicated after preprocessing
duplicated_count = df.duplicated().sum()
print("Number of duplicate entries: ", duplicated_count)

# let's drop all duplicated reviews
df = df.drop_duplicates('review')

# let's count the words in each review again
df['new word count'] = df['review'].apply(count_words)

# encoding the sentiment
df.sentiment.replace("positive", 1, inplace=True)
df.sentiment.replace("negative", 0, inplace=True)

df.head()

#word cloud for positive review words
pos_reviews =  df[df.sentiment == 1]
pos_reviews.head()

text = ' '.join([word for word in pos_reviews['review']])
plt.figure(figsize=(20,15), facecolor='None')
wordcloud = WordCloud(max_words=500, width=1600, height=800).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most frequent words in positive reviews', fontsize = 19)
plt.show()

# print the first 10th most common words
from collections import Counter
count = Counter()
for text in pos_reviews['review'].values:
    for word in text.split():
        count[word] +=1
count.most_common(10)

#word cloud for negitive review words
neg_reviews =  df[df.sentiment == 0]
neg_reviews.head()

text = ' '.join([word for word in neg_reviews['review']])
plt.figure(figsize=(20,15), facecolor='None')
wordcloud = WordCloud(max_words=500, width=1600, height=800).generate(text)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Most frequent words in negitive reviews', fontsize = 19)
plt.show()

# print the first 10th most common words
from collections import Counter
count = Counter()
for text in neg_reviews['review'].values:
    for word in text.split():
        count[word] +=1
count.most_common(10)

"""# **Splitting data**"""

X = df['review']
Y = df['sentiment']

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)

# Term Frequency-Inverse Document Frequency model (TFIDF)
# It is used to convert text documents to matrix of tfidf features
vect = TfidfVectorizer()
x_train = vect.fit_transform(x_train)
x_test = vect.transform(x_test)

print("Size of x_train: ", (x_train.shape))
print("Size of y_train: ", (y_train.shape))
print("Size of x_test: ", (x_test.shape))
print("Size of y_test: ", (y_test.shape))

"""# **Evaluation**
We will use several machine learning models to do different tests and select the best
"""

from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# LogisticRegression
lr = LogisticRegression()
lr.fit(x_train, y_train)
print("train score : ", lr.score(x_train, y_train))
print("test score : ", lr.score(x_test, y_test))
lr_pred = lr.predict(x_test)
lr_acc = accuracy_score(lr_pred, y_test)
print("Test accuracy: {:.2f}%".format(lr_acc*100))

lr_report=classification_report(y_test,lr_pred,target_names=['Positive','Negative'])
print(lr_report)

def cm (y_test,y_pred):
  cm = confusion_matrix(y_test, y_pred)
  cm_matrix = pd.DataFrame(data=cm, columns=['Actual Positive:1', 'Actual Negative:0'], 
                                  index=['Predict Positive:1', 'Predict Negative:0'])
  sns.heatmap(cm_matrix, annot=True, fmt='d', cmap='YlGnBu')

cm(y_test,lr_pred)
plt.title('Confusion matrix of Logistic Regression')

# Linear svm
lsvm = LinearSVC()
lsvm.fit(x_train, y_train)
print("train score : ", lsvm.score(x_train, y_train))
print("test score : ", lsvm.score(x_test, y_test))
lsvm_pred = lsvm.predict(x_test)
lsvm_acc = accuracy_score(lsvm_pred, y_test)
print("Test accuracy: {:.2f}%".format(lsvm_acc*100))

lsvm_report=classification_report(y_test,lsvm_pred,target_names=['Positive','Negative'])
print(lsvm_report)

cm(y_test,lsvm_pred)
plt.title('Confusion matrix of LinearSVC')

# MultinomialNB
mn = MultinomialNB()
mn.fit(x_train, y_train)
print("train score : ", mn.score(x_train, y_train))
print("test score : ", mn.score(x_test, y_test))
mn_pred = mn.predict(x_test)
mn_acc = accuracy_score(mn_pred, y_test)
print("Test accuracy: {:.2f}%".format(mn_acc*100))

mn_report=classification_report(y_test,mn_pred,target_names=['Positive','Negative'])
print(mn_report)

cm(y_test,mn_pred)
plt.title('Confusion matrix of MultinomialNB')

# DecisionTreeClassifier
dt = DecisionTreeClassifier()
dt.fit(x_train, y_train)
print("train score : ", dt.score(x_train, y_train))
print("test score : ", dt.score(x_test, y_test))
dt_pred = dt.predict(x_test)
dt_acc = accuracy_score(dt_pred, y_test)
print("Test accuracy: {:.2f}%".format(dt_acc*100))

dt_report=classification_report(y_test,mn_pred,target_names=['Positive','Negative'])
print(dt_report)

cm(y_test,dt_pred)
plt.title('Confusion matrix of Decision Tree Classifier')

# comparison betweem different ml algorithms
comp = {'Algorithm': ['Logistic Regression', 'MultinomialNB','LinearSVC','DecisionTreeClassifier'], 'Test Accuracy': [lr_acc*100, mn_acc*100,lsvm_acc*100,dt_acc*100]}
pd.DataFrame(data=comp)