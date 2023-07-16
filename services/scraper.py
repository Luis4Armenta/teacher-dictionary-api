from abc import ABC
from requests import Response
from typing import Optional, List
from statistics import mean, stdev

import bs4
import requests
from lxml import etree

from models.teacher import Teacher, Comment

from services.text_analyzer.text_analyzer import TextAnalyzer

from utils.text import get_url_for_teacher
from utils.metrics import get_positive_score

class WebScraper(ABC):
  def find_teacher(self, name: str) -> Optional[Teacher]:
    pass

# name: '//h5//span/text()'
# subjects: '//span[@class="bluetx negritas"]/text()'
# raw_comments: '//div[@class="p-4 box-profe bordeiz"]'
  # text: './/p[@class="comentario"]/text()'
  # date: './/p[@class="fecha"]/text()'
  # likes: './/a[@rel="like"]//span/text()'
  # dislikes: './/a[@rel="nolike"]//span/text()' 

class BS4WebScraper(WebScraper):
  def __init__(self, text_analyzer: TextAnalyzer):
    self.text_analyzer = text_analyzer
  
  def find_teacher(self, name: str) -> Optional[Teacher]:
    if name == 'SIN ASIGNAR':
      return Teacher(
        id=None,
        name='SIN ASIGNAR',
        comments=[],
        subjects=[],
        positive_score=0.5,
        url='https://foroupiicsa.net/diccionario/'
      )
    
    url = self.get_url_for_teacher(name.upper())
    response: Response = requests.get(url)
    response.raise_for_status()

    if response.status_code == 200:
      soup = bs4.BeautifulSoup(response.content, 'html.parser')
      dom = etree.HTML(str(soup))
      
      name = dom.xpath('//h5//span/text()')[0].upper()
      
      subjs: List[str] = dom.xpath('//span[@class="bluetx negritas"]/text()')
      subjs = [subj.strip().upper() for subj in subjs]
      subjs = list(set(subjs))
      subjects: List[str] = subjs
      
      if len(subjects) == 0:
        return None


      positive_scores: List[float] = []
      comments: List[Comment] = []
      
      
      raw_comments = dom.xpath('//div[@class="p-4 box-profe bordeiz"]')
      
      for raw_comment in raw_comments:
        subject: str = raw_comment.xpath('.//span[@class="bluetx negritas"]/text()')[0]
        text: str = raw_comment.xpath('.//p[@class="comentario"]/text()')[0]
        likes: int = int(raw_comment.xpath('.//a[@rel="like"]//span/text()')[0])
        dislikes: int = int(raw_comment.xpath('.//a[@rel="nolike"]//span/text()')[0])
        date: str = raw_comment.xpath('.//p[@class="fecha"]/text()')[0]
        
        positive_score, negative_score, neutral_score= self.text_analyzer.analyze_sentiment(text)
        
        neutral_score_rate = 0.85
        positive_scores.append(positive_score + (neutral_score * neutral_score_rate))
        
        comment: Comment = {
          'subject': subject,
          'text': text,
          'likes': likes,
          'dislikes': dislikes,
          'date': date,
          'positive_score': positive_score,
          'neutral_score': neutral_score,
          'negative_score': negative_score,
        }
        
        comments.append(comment)
        
      
      teacher: Teacher = Teacher(
        _id=None,
        name=name,
        url=url,
        subjects=subjects,
        comments=comments,
        positive_score=get_positive_score(positive_scores)
      )
      
      return teacher
    else:
      return None


