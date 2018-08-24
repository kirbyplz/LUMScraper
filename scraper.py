from selenium import webdriver
#http://stanford.edu/~mgorkove/cgi-bin/rpython_tutorials/Scraping_a_Webpage_Rendered_by_Javascript_Using_Python.php

class scraper:
  def getter(url):
    browser = webdriver.Chrome() #replace with .Firefox(), or with the browser of your choice
    browser.get(url) #navigate to the page
    #innerHTML = browser.execute_script("return document.body.innerHTML") #returns the inner HTML as a string

