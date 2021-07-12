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
using NodaTime;
using ProtoBuf;
using System.IO;
using QuantConnect.Data;
using System.Collections.Generic;
using Newtonsoft.Json;
using DateTimeUtilityFunctions = QuantConnect.Securities.Future.FuturesExpiryUtilityFunctions;

namespace QuantConnect.DataSource
{
    /// <summary>
    /// Regalytics Regulatory articles
    /// </summary>
    [ProtoContract(SkipConstructor = true)]
    public class RegalyticsRegulatoryArticle : BaseData
    {
        private DateTime _endTime;

        /// <summary>
        /// Data source ID
        /// </summary>
        public static int DataSourceId { get; } = 2030;

        [JsonProperty(PropertyName = "id")]
        public int Id { get; set; }

        [JsonProperty(PropertyName = "title")]
        public string Title { get; set; }

        [JsonProperty(PropertyName = "summary")]
        public string Summary { get; set; }

        [JsonProperty(PropertyName = "status")]
        public string Status { get; set; }

        [JsonProperty(PropertyName = "classification")]
        public string Classification { get; set; }

        [JsonProperty(PropertyName = "filing_type")]
        public string FilingType { get; set; }

        [JsonProperty(PropertyName = "in_federal_register")]
        public bool InFederalRegister { get; set; }

        [JsonProperty(PropertyName = "federal_register_number")]
        public string FederalRegisterNumber { get; set; }

        //[JsonProperty(PropertyName = "regalytics_alert_id")]
        //public string AlertId { get; set; }

        [JsonProperty(PropertyName = "proposed_comments_due_date")]
        public DateTime? ProposedCommentsDueDate { get; set; }

        [JsonProperty(PropertyName = "original_publication_date")]
        public DateTime? OriginalPublicationDate { get; set; }

        [JsonProperty(PropertyName = "federal_register_publication_date")]
        public DateTime? FederalRegisterPublicationDate { get; set; }

        [JsonProperty(PropertyName = "rule_effective_date")]
        public DateTime? RuleEffectiveDate { get; set; }

        [JsonProperty(PropertyName = "latest_update")]
        public DateTime LatestUpdate { get; set; }

        [JsonProperty(PropertyName = "alert_type")]
        public string AlertType { get; set; }

        [JsonProperty(PropertyName = "states")]
        public Dictionary<string, List<string>> States { get; set; }

        [JsonProperty(PropertyName = "agencies")]
        public List<string> Agencies { get; set; }

        [JsonProperty(PropertyName = "pdf_url")]
        public string AnnouncementUrl { get; set; }

        public override DateTime EndTime
        {
            get { return _endTime; }
            set { _endTime = value; }
        }

        /// <summary>
        /// Return the URL string source of the file. This will be converted to a stream
        /// </summary>
        /// <param name="config">Configuration object</param>
        /// <param name="date">Date of this source file</param>
        /// <param name="isLiveMode">true if we're in live mode, false for backtesting mode</param>
        /// <returns>String URL of source file.</returns>
        public override SubscriptionDataSource GetSource(SubscriptionDataConfig config, DateTime date, bool isLiveMode)
        {
            var publicationDate = DateTimeUtilityFunctions.AddBusinessDays(date.Date, -1, false);

            return new SubscriptionDataSource(
                Path.Combine(
                    Globals.DataFolder,
                    "alternative",
                    "regalytics",
                    "articles",
                    $"{publicationDate:yyyyMMdd}.json"
                ),
                SubscriptionTransportMedium.LocalFile
            );
        }

        /// <summary>
        /// Parses the data from the line provided and loads it into LEAN
        /// </summary>
        /// <param name="config">Subscription configuration</param>
        /// <param name="line">Line of data</param>
        /// <param name="date">Date</param>
        /// <param name="isLiveMode">Is live mode</param>
        /// <returns>New instance</returns>
        public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, bool isLiveMode)
        {
            var article = JsonConvert.DeserializeObject<RegalyticsRegulatoryArticle>(line);

            // date == the day that the data was published (2021-05-21)
            // 2021-05-21 for example, contains aggregated data from 2021-05-19, 2021-05-20. 
            // Regalytics publishes at around 07:30:00 Eastern Time, but is downloaded by
            // us around 08:00:00 Eastern Time.

            article.Symbol = config.Symbol;
            article.Time = article.LatestUpdate;
            article.EndTime = DateTimeUtilityFunctions.AddBusinessDays(article.LatestUpdate.Date, 1, false).AddHours(8);

            return article;
        }

        /// <summary>
        /// Clones the data
        /// </summary>
        /// <returns>A clone of the object</returns>
        public override BaseData Clone()
        {
            return new RegalyticsRegulatoryArticle
            {
                Symbol = Symbol,
                Time = Time,
                EndTime = EndTime,

                Id = Id,
                Title = Title,
                Summary = Summary,
                Status = Status,
                Classification = Classification,
                FilingType = FilingType,
                InFederalRegister = InFederalRegister,
                FederalRegisterNumber = FederalRegisterNumber,
                // AlertId = AlertId,
                ProposedCommentsDueDate = ProposedCommentsDueDate,
                OriginalPublicationDate = OriginalPublicationDate,
                FederalRegisterPublicationDate = FederalRegisterPublicationDate,
                RuleEffectiveDate = RuleEffectiveDate,
                LatestUpdate = LatestUpdate,
                AlertType = AlertType,
                States = States,
                Agencies = Agencies,
                AnnouncementUrl = AnnouncementUrl,
            };
        }

        /// <summary>
        /// Indicates whether the data source is tied to an underlying symbol and requires that corporate events be applied to it as well, such as renames and delistings
        /// </summary>
        /// <returns>false</returns>
        public override bool RequiresMapping()
        {
            return false;
        }

        /// <summary>
        /// Indicates whether the data is sparse.
        /// If true, we disable logging for missing files
        /// </summary>
        /// <returns>true</returns>
        public override bool IsSparseData()
        {
            return true;
        }

        /// <summary>
        /// Converts the instance to string
        /// </summary>
        public override string ToString()
        {
            return $"ID: {Id} - Title: {Title} - Summary: {Summary}";
        }

        /// <summary>
        /// Gets the default resolution for this data and security type
        /// </summary>
        public override Resolution DefaultResolution()
        {
            return Resolution.Daily;
        }

        /// <summary>
        /// Gets the supported resolution for this data and security type
        /// </summary>
        public override List<Resolution> SupportedResolutions()
        {
            return DailyResolution;
        }

        /// <summary>
        /// Specifies the data time zone for this data type. This is useful for custom data types
        /// </summary>
        /// <returns>The <see cref="T:NodaTime.DateTimeZone" /> of this data type</returns>
        public override DateTimeZone DataTimeZone()
        {
            return TimeZones.NewYork;
        }
    }
}