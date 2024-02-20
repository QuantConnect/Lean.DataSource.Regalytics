/*
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

        [Test]
        public void BackwardCompatibilityToV2()
        {
            // The Id is a number in v2
            var line = "{\"id\": 2051381, \"title\": \"House of Representatives Study Bill HSB692: A bill for an act relating to school security, including by modifying provisions related to the issuance of school bonds, requiring schools to conduct school safety reviews and have access to the statewide interoperable communications system, establishing the school emergency radio access grant program and the firearm detection software grant program within the department of homeland security and emergency management, requiring the department of public (I)\", \"summary\": \"Introduced on 2024-02-12. House Study Bill 692 is a piece of legislation in Iowa that focuses on school security. It includes provisions related to the issuance of school bonds, requires schools to conduct safety reviews and have access to a statewide communications system, establishes grant programs for school emergency radio access and firearm detection software, and requires the Department of Public Safety to convene a task force on school safety standards. The bill also appropriates funds for these programs and specifies that the state cost of compliance with the legislation will be paid by school districts from state school foundation aid. The bill takes effect upon enactment. (99IA202320242022HSB692)\", \"status\": \"New\", \"classification\": \"State\", \"filing_type\": \"Single\", \"in_federal_register\": false, \"federal_register_number\": null, \"regalytics_alert_id\": \"99IA2022HSB69225120240212\", \"proposed_comments_due_date\": null, \"original_publication_date\": \"2024-02-12\", \"federal_register_publication_date\": null, \"rule_effective_date\": null, \"latest_update\": \"2024-02-12\", \"alert_type\": \"Study Bill\", \"docket_file_number\": \"\", \"order_notice\": \"\", \"sec_release_number\": \"\", \"agencies\": [\"Iowa House of Representatives\"], \"sector_type\": [{\"name\": \"Financial\"}], \"tags\": [{\"name\": \"All State and Federal Legislatures\"}, {\"name\": \"Introduced Bill\"}], \"subtype_classification\": [{\"name\": \"House of Representatives Study Bill\", \"higher_order_alert_classification\": {\"name\": \"Rule\"}}], \"pdf_url\": \"https://www.legis.iowa.gov/legislation/BillBook?ga=90&ba=HSB692\", \"created_at\": \"2024-02-12T22:31:40.567008\", \"states\": {\"United States\": [\"Iowa\"]}}";
            var instance = new RegalyticsRegulatoryArticle();
            var config = new SubscriptionDataConfig(instance.GetType(), Symbol.None, Resolution.Daily, TimeZones.Utc, TimeZones.Utc, false, false, false);
            var data = instance.Reader(config, line, new DateTime(2024, 2, 12), false) as RegalyticsRegulatoryArticle;
            Assert.AreEqual("2051381", data.Id);
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

                Id = "0",
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

                    Id = "0",
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

                    Id = "0",
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