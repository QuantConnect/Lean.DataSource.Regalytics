#  QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
#  Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from AlgorithmImports import *

### <summary>
### Example algorithm using the Regalytics data as a source of alpha
### </summary>
class RegalyticsDataAlgorithm(QCAlgorithm): 
    def Initialize(self):
        ''' Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''
        self.SetStartDate(2022, 7, 10)
        self.SetEndDate(2022, 7, 15)
        self.SetCash(100000);
        
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
            
        # Requesting data
        self.regalyticsSymbol = self.AddData(RegalyticsRegulatoryArticles, "REG").Symbol
            
        # Historical data
        history = self.History(self.regalyticsSymbol, 7, Resolution.Daily)
        self.Debug(f"We got {len(history)} items from our history request")

    def OnData(self, slice):
        ''' OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        :param Slice slice: Slice object keyed by symbol containing the stock data
        '''
        data = slice.Get(RegalyticsRegulatoryArticles)
        if not data: return
        
        for articles in data.Values:
            self.Log(articles.ToString())
            
            for article in articles:
                article = RegalyticsRegulatoryArticle(article)
                
                # based on the custom data property we will buy or short the underlying equity
                if any([p in article.Title.lower() for p in self.negative_sentiment_phrases]):
                    self.SetHoldings(self.symbol, -1)
                else:
                    self.SetHoldings(self.symbol, 1)