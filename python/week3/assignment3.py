# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 20:53:36 2018

@author: khalid
"""
import pandas as pd
import numpy as np

def handle_dataset():
    """ Handling the datasets and return useful dataframes """
    energy = pd.read_excel('Energy Indicators.xls',na_values='...')
    energy = energy.iloc[16:243,2:]
    energy.columns = ['Country', 'Energy Supply', 'Energy Supply per Capita', '% Renewable']
    energy = energy.astype({'Energy Supply':float, 'Energy Supply per Capita':float, '% Renewable':float})
    energy.Country = energy.Country.str.replace(r'\d','').str.replace('(','').str.replace(')','')
    countries = {'Republic of Korea': 'South Korea','United States of America': 'United States','United Kingdom of Great Britain and Northern Ireland': 'United Kingdom','China, Hong Kong Special Administrative Region': 'Hong Kong'}
    energy['Country'] = energy['Country'].replace(countries)
    energy['Energy Supply'] = energy['Energy Supply'] * 1000000
    
    gdp = pd.read_csv('world_bank.csv',skiprows=4,header=0)
    countries_gdp = {"Korea, Rep.": "South Korea", "Iran, Islamic Rep.": "Iran","Hong Kong SAR, China": "Hong Kong"}
    gdp['Country Name'].replace(countries_gdp,inplace=True)
    
    ScimEn = pd.read_excel("scimagojr.xlsx")
    return energy,gdp,ScimEn
energy,gdp,ScimEn = handle_dataset()

def answer_one(howw='outer'):
    """ return a DataFrame with 20 columns and 15 entries """
    energy,gdp,ScimEn = handle_dataset()
    df = energy.merge(ScimEn,on='Country',how=howw).merge(gdp,left_on='Country',right_on='Country Name',how=howw)
    df = df.loc[df['Rank'].isin([i for i in range(1,16)]),['Country','Rank', 'Documents', 'Citable documents', 'Citations', 'Self-citations', 'Citations per document', 'H index', 'Energy Supply', 'Energy Supply per Capita', '% Renewable', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015']]
    df.set_index('Country',inplace =True)
    df.sort_values(by='Rank',inplace=True)
    return df

answer_one()

def answer_two():
    """ Number of entries losed when use inner join instead of outer """
    energy,gdp,ScimEn = handle_dataset()
    df_union = energy.merge(ScimEn,on='Country',how='outer').merge(gdp,left_on='Country',right_on='Country Name',how='outer')
    df_intersect = energy.merge(ScimEn,on='Country',how='inner').merge(gdp,left_on='Country',right_on='Country Name',how='inner')    
    entries = len(df_union) - len(df_intersect)
    return entries
answer_two()


def answer_three():
    """ Average GDP over the last 10 years for each country """
    Top15 = answer_one()
    avgGDP = Top15.loc[:,'2006':'2015'].mean(axis=1)
    return avgGDP
answer_three()


def answer_four():
    """ How much had the GDP changed over the 10 year span for the country with the 6th largest average GDP """
    Top15 = answer_three()
    Top15.sort_values(inplace=True,ascending=False)
    country = Top15.index[6]
    df = answer_one().loc[country,['2006','2015']]
    change = df['2015']-df['2006']
    return change
answer_four()


def answer_five():
    """ the mean Energy Supply per Capita """
    return answer_one('inner')['Energy Supply per Capita'].mean()
answer_five()


def answer_six():
    """ country has the maximum % Renewable and what is the percentage """
    country = answer_one().loc[:,'% Renewable'].idxmax()
    percentage = answer_one()['% Renewable'].max()
    return country,percentage
answer_six()


def answer_seven():
    """ Create a new column that is the ratio of Self-Citations to Total Citations.
        return a tuple with the name of the highest ratio country and the ratio.
    """
    df = answer_one().loc[:,['Self-citations','Citations']]
    df['ratio'] = df['Self-citations']/df['Citations']
    country = df['ratio'].idxmax()
    percentage = df['ratio'].max()
    return country,percentage
answer_seven()


def answer_eight():
    """  Create a column that estimates the population using Energy Supply 
    and Energy Supply per capita. What is the third most populous country
     according to this estimate?
    """
    df = answer_one('inner').loc[:,['Energy Supply','Energy Supply per Capita']]
    df['pop'] = df['Energy Supply'].divide(df['Energy Supply per Capita'])
    country = df['pop'].nlargest(3).index[2]
    return country
answer_eight()


def answer_nine():
    """
    Create a column that estimates the number of citable documents per person.
    What is the correlation between the number of citable documents per
    capita and the energy supply per capita
    """
    df = answer_one('inner')
    df['pop'] = df['Energy Supply'].divide(df['Energy Supply per Capita'])
    df['CDP']=df['Citable documents']/df['pop']
    correlation = df['CDP'].corr(df['Energy Supply per Capita'],method='pearson')
    return correlation
answer_nine()


def plot9():    
    Top15 = answer_one('inner')
    Top15['PopEst'] = Top15['Energy Supply'] / Top15['Energy Supply per Capita']
    Top15['Citable docs per Capita'] = Top15['Citable documents'] / Top15['PopEst']
    Top15.plot(x='Citable docs per Capita', y='Energy Supply per Capita', kind='scatter', xlim=[0, 0.0006])
    
plot9() # Be sure to comment out plot9() before submitting the assignment!


def answer_ten():
    """ Create a new column with a 1 if the country's % Renewable value
    is at or above the median for all countries in the top 15,
    and a 0 if the country's % Renewable value is below the median. """
    df = answer_one()
    threshold = df['% Renewable'].median()
    HighRenew = pd.Series([1 if item >= threshold else 0 for item in df['% Renewable']],name='HighRenew',index=df.index)
    return HighRenew
answer_ten()


def answer_eleven():
    df = answer_one('inner')
    df['population']=df['Energy Supply']/df['Energy Supply per Capita']
    df['population'] = np.float64(df['population'])
    ContinentDict = {'China':'Asia', 'United States':'North America', 'Japan':'Asia', 'United Kingdom':'Europe', 'Russian Federation':'Europe', 'Canada':'North America',
 'Germany':'Europe',
 'India':'Asia',
 'France':'Europe',
 'South Korea':'Asia',
 'Italy':'Europe',
 'Spain':'Europe',
 'Iran':'Asia',
 'Australia':'Australia',
 'Brazil':'South America'}
    df.rename(index=ContinentDict,inplace=True)
    df.reset_index(inplace = True)
    functions = ['size', 'sum', 'mean', 'std']
    result = df[['Country','population']].groupby('Country').agg(functions)
    return(result)
answer_eleven()


def answer_twelve():
    """Cut % Renewable into 5 bins. Group Top15 by the Continent,
    as well as these new % Renewable bins. How many countries are in each of these groups?
    This function should return a Series with a MultiIndex of Continent,
    then the bins for % Renewable. Do not include groups with no countries
    """
    df = answer_one()
    ContinentDict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}
    df['bin'] = pd.cut(df['% Renewable'],5)
    df = df.groupby([ContinentDict,'bin'])['Rank'].count()
    return df
answer_twelve()


def answer_thirteen():
    """ Convert the Population Estimate series to a string with thousands separator 
    (using commas). Do not round the results. """
    df = answer_one('inner')
    df['pop'] = df['Energy Supply'].divide(df['Energy Supply per Capita'])
    df['PopEst'] = df['pop'].apply(lambda x : format(x,','))
    return df['PopEst']
answer_thirteen()


def plot_optional():
    Top15 = answer_one('inner')
    ax = Top15.plot(x='Rank', y='% Renewable', kind='scatter', 
                    c=['#e41a1c','#377eb8','#e41a1c','#4daf4a','#4daf4a','#377eb8','#4daf4a','#e41a1c',
                       '#4daf4a','#e41a1c','#4daf4a','#4daf4a','#e41a1c','#dede00','#ff7f00'], 
                    xticks=range(1,16), s=6*Top15['2014']/10**10, alpha=.75, figsize=[16,6]);

    for i, txt in enumerate(Top15.index):
        ax.annotate(txt, [Top15['Rank'][i], Top15['% Renewable'][i]], ha='center')

    print("""This is an example of a visualization that can be created to help understand the data.This is a bubble chart showing % Renewable vs.
          Rank. The size of the bubble corresponds to the countries'2014 GDP,
          and the color corresponds to the continent.""")

plot_optional()