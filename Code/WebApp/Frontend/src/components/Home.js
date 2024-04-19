import React, { useState } from "react";
import { TableauEmbed } from "@stoddabr/react-tableau-embed-live";

const Home = () => {
  const [activeTab, setActiveTab] = useState("overview");

  const competitorUrl =
    "https://public.tableau.com/views/CompetitorAnalysis_17127319838040/CompetitorAnalysis?:language=en-US&publish=yes&:sid=&:display_count=n&:origin=viz_share_link";
  const overviewUrl =
    "https://public.tableau.com/shared/RRS6NDK8J?:display_count=n&:origin=viz_share_link";
  const parkingUrl =
    "https://public.tableau.com/views/CommonDashboard_17127262051290/ParkingDashboard?:language=en-US&publish=yes&:sid=&:display_count=n&:origin=viz_share_link";
  const propertyUrl =
    "https://public.tableau.com/views/CommonDashboard_17127262051290/ListingsDashboard?:language=en-US&publish=yes&:sid=&:display_count=n&:origin=viz_share_link";
  const builderUrl =
    "https://public.tableau.com/views/BuilderDashboard_17127297372520/BuildersDashboard?:language=en-US&publish=yes&:sid=&:display_count=n&:origin=viz_share_link";

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="container w-75 pt-5 pb-2 px-0">
      <ul className="nav nav-tabs fs-9 mx-3" id="myTab" role="tablist">
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => handleTabChange("overview")}
          >
            Overview
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === "listing" ? "active" : ""}`}
            onClick={() => handleTabChange("listing")}
          >
            Listing
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === "competitor" ? "active" : ""}`}
            onClick={() => handleTabChange("competitor")}
          >
            Competitor Analysis
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === "parking" ? "active" : ""}`}
            onClick={() => handleTabChange("parking")}
          >
            Parking
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === "builder" ? "active" : ""}`}
            onClick={() => handleTabChange("builder")}
          >
            Builder
          </button>
        </li>
      </ul>
      <div
        className="tab-content  d-flex justify-content-center"
        id="myTabContent"
      >
        <div
          className={`tab-pane fade ${
            activeTab === "overview" ? "show active" : ""
          }`}
          id="overview"
          role="tabpanel"
        >
          {activeTab === "overview" && (
            <div className="tableau-container">
              <TableauEmbed sourceUrl={overviewUrl} />
            </div>
          )}
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "listing" ? "show active" : ""
          }`}
          id="listing"
          role="tabpanel"
        >
          {activeTab === "listing" && (
            <div className="tableau-container">
              <TableauEmbed sourceUrl={propertyUrl} />
            </div>
          )}
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "competitor" ? "show active" : ""
          }`}
          id="competitor"
          role="tabpanel"
        >
          {activeTab === "competitor" && (
            <div className="tableau-container">
              <TableauEmbed sourceUrl={competitorUrl} />
            </div>
          )}
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "parking" ? "show active" : ""
          }`}
          id="parking"
          role="tabpanel"
        >
          {activeTab === "parking" && (
            <div className="tableau-container">
              <TableauEmbed sourceUrl={parkingUrl} />
            </div>
          )}
        </div>
        <div
          className={`tab-pane fade ${
            activeTab === "builder" ? "show active" : ""
          }`}
          id="builder"
          role="tabpanel"
        >
          {activeTab === "builder" && (
            <div className="tableau-container">
              <TableauEmbed sourceUrl={builderUrl} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
