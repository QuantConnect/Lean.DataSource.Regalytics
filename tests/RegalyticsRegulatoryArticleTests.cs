﻿/*
 * QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
 * Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
*/

using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using NUnit.Framework;
using QuantConnect.Data;
using QuantConnect.DataSource;

namespace QuantConnect.DataLibrary.Tests
{
    [TestFixture]
    public class RegalyticsRegulatoryArticleTests
    {
        [Test]
        public void JsonRoundTrip()
        {
            var expected = CreateNewInstance();
            var type = expected.GetType();
            var serialized = JsonConvert.SerializeObject(expected);
            var result = JsonConvert.DeserializeObject(serialized, type);

            AssertAreEqual(expected, result);
        }

        [Test]
        public void Clone()
        {
            var expected = CreateNewInstance();
            var result = expected.Clone();

            AssertAreEqual(expected, result);
        }

        [Test]
        public void CloneCollection()
        {
            var expected = CreateNewCollectionInstance();
            var result = expected.Clone();

            AssertAreEqual(expected, result);
        }
        
        private void AssertAreEqual(object expected, object result, bool filterByCustomAttributes = false)
        {
            foreach (var propertyInfo in expected.GetType().GetProperties())
            {
                // we skip Symbol which isn't protobuffed
                if (filterByCustomAttributes && propertyInfo.CustomAttributes.Count() != 0)
                {
                    Assert.AreEqual(propertyInfo.GetValue(expected), propertyInfo.GetValue(result));
                }
            }
            foreach (var fieldInfo in expected.GetType().GetFields())
            {
                Assert.AreEqual(fieldInfo.GetValue(expected), fieldInfo.GetValue(result));
            }
        }

        private BaseData CreateNewInstance()
        {
            return new RegalyticsRegulatoryArticle
            {
                Symbol = Symbol.Empty,
                Time = DateTime.Today,
                DataType = MarketDataType.Base,

                Id = 0,
                Title = "string",
                Summary = "string",
                Status = "string",
                Classification = "string",
                FilingType = "string",
                InFederalRegister = true,
                FederalRegisterNumber = "string",
                ProposedCommentsDueDate = DateTime.MinValue,
                OriginalPublicationDate = DateTime.MinValue,
                FederalRegisterPublicationDate = DateTime.MinValue,
                RuleEffectiveDate = DateTime.MinValue,
                LatestUpdate = DateTime.MinValue,
                AlertType = "string",
                States = new Dictionary<string, List<string>> { {"string", new List<string>{"string"}} },
                Agencies = new List<string>{"string"},
                AnnouncementUrl = "string",
                CreatedAt = DateTime.MinValue
            };
        }

        private BaseData CreateNewCollectionInstance()
        {
            return new RegalyticsRegulatoryArticles
            {
                new RegalyticsRegulatoryArticle
                {
                    Symbol = Symbol.Empty,
                    Time = DateTime.Today,
                    DataType = MarketDataType.Base,

                    Id = 0,
                    Title = "string",
                    Summary = "string",
                    Status = "string",
                    Classification = "string",
                    FilingType = "string",
                    InFederalRegister = true,
                    FederalRegisterNumber = "string",
                    ProposedCommentsDueDate = DateTime.MinValue,
                    OriginalPublicationDate = DateTime.MinValue,
                    FederalRegisterPublicationDate = DateTime.MinValue,
                    RuleEffectiveDate = DateTime.MinValue,
                    LatestUpdate = DateTime.MinValue,
                    AlertType = "string",
                    States = new Dictionary<string, List<string>> { {"string", new List<string>{"string"}} },
                    Agencies = new List<string>{"string"},
                    AnnouncementUrl = "string",
                    CreatedAt = DateTime.MinValue
                },
                new RegalyticsRegulatoryArticle
                {
                    Symbol = Symbol.Empty,
                    Time = DateTime.Today,
                    DataType = MarketDataType.Base,

                    Id = 0,
                    Title = "string",
                    Summary = "string",
                    Status = "string",
                    Classification = "string",
                    FilingType = "string",
                    InFederalRegister = true,
                    FederalRegisterNumber = "string",
                    ProposedCommentsDueDate = DateTime.MinValue,
                    OriginalPublicationDate = DateTime.MinValue,
                    FederalRegisterPublicationDate = DateTime.MinValue,
                    RuleEffectiveDate = DateTime.MinValue,
                    LatestUpdate = DateTime.MinValue,
                    AlertType = "string",
                    States = new Dictionary<string, List<string>> { {"string", new List<string>{"string"}} },
                    Agencies = new List<string>{"string"},
                    AnnouncementUrl = "string",
                    CreatedAt = DateTime.MinValue
                }
            };
        }
    }
}