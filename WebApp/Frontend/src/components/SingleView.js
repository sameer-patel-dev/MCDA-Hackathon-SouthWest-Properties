import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { MdOutlineEventNote } from "react-icons/md";
import { BsFillLampFill } from "react-icons/bs";
import { BiDetail } from "react-icons/bi";
import { FaLocationDot } from "react-icons/fa6";
import { instance } from "../config/config";
import { MdLocalGroceryStore, MdMovie, MdEmergencyShare } from "react-icons/md";
import { GiBookshelf, GiCrimeSceneTape } from "react-icons/gi";
import {
  CircularProgressbar,
  buildStyles,
  CircularProgressbarWithChildren,
} from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import noImg from "../assets/img/no-img.jpg";
const SingleView = () => {
  const location = useLocation();
  const id = location?.state;

  const [item, setItem] = useState(null);
  // const [position, setPosition] = useState(null);

  const icon = L.icon({
    iconUrl:
      "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  });

  useEffect(() => {
    instance
      .get(`api/listing/${id}`)
      .then((res) => {
        setItem(res?.data);
        // setPosition([res?.data?.listingLatitude, res?.data?.listingLongitude]);
      })
      .catch((err) => {
        console.log(err);
      });
  }, [id]);

  const getAllperks = (label) => {
    let message = "";
    let perks = [];
    return (
      <div className={`${label} custom-bottom my-3`}>
        <span className="fs-8">{label}</span>

        <div className="d-flex">
          {item &&
            Object.keys(item)?.map((field, idx) => {
              if (
                field?.includes(label) &&
                (item[field] === "True" || item[field] === "1")
              ) {
                const matches = field.match(/([a-zA-Z]+)([A-Z][a-z]+)/);
                perks = matches[1];
                return (
                  <p
                    key={idx}
                    className="border-primary-color rounded-pill p-1 px-3 fs-8 me-2 my-1"
                  >
                    {matches && matches[1]}{" "}
                    {/* Displaying the first part of the split field */}
                  </p>
                );
              } else {
                message = `Sorry, no ${label} included.`;
                return null; // Return null if the conditions are not met
              }
            })}
        </div>
        <p className="fs-9 mb-2 fw-normal text-secondary">
          {perks?.length == 0 && message}
        </p>
      </div>
    );
  };

  const getAllScores = (type, item) => {
    let label = type && type.toLowerCase();
    let value =
      type !== "crime"
        ? parseInt(item).toFixed(2)
        : item === "Very_Safe"
        ? 90
        : item === "Safe"
        ? 75
        : item === "Risky"
        ? 50
        : item === "Dangerous"
        ? 20
        : "";
    return (
      <div className="d-flex flex-column justify-content-start align-items-center ms-4 mb-3">
        <div className="scoreIcon mb-1">
          {label === "grocery" ? (
            <MdLocalGroceryStore />
          ) : label === "recreation" ? (
            <MdMovie />
          ) : label === "education" ? (
            <GiBookshelf />
          ) : label === "emergency" ? (
            <MdEmergencyShare />
          ) : label == "crime" ? (
            <GiCrimeSceneTape />
          ) : (
            ""
          )}
        </div>
        <span className="text-capitalize fs-9 mb-2">{type} Score</span>

        <div class="" style={{ width: 60, height: 60, fontWeight: "bold" }}>
          <CircularProgressbar
            value={value}
            text={type === "crime" ? item?.replace("_", " ") : value}
            styles={buildStyles({
              // Text size
              textSize: type === "crime" ? "20px" : "22px",
              fontWeight: "bold",
              // Colors
              pathColor:
                type === "crime" ? (value > 50 ? "#c1cd23" : "red") : "#c1cd23",
              textColor:
                type === "crime" ? (value > 50 ? "#000" : "red") : "#000",
            })}
          />
        </div>
      </div>
    );
  };

  return (
    <>
      <div className="container">
        <div className="row">
          <div className="col-lg-12">
            <div className="d-flex flex-wrap justify-content-center between align-items-center p-4 ">
              <div className="detailedView mb-3">
                <img
                  src={
                    item?.imageLink?.match(/\.(jpeg|jpg|gif|png)$/) !== null
                      ? item?.imageLink
                      : noImg
                  }
                  className="position-relative"
                />
              </div>

              <div className=" ms-4 shadow">
                <ul
                  class="nav nav-pills mb-3 rounded-top"
                  id="pills-tab"
                  role="tablist"
                >
                  <li class="nav-item " role="presentation">
                    <button
                      class="nav-link active rounded"
                      id="pills-home-tab"
                      data-bs-toggle="pill"
                      data-bs-target="#pills-home"
                      type="button"
                      role="tab"
                      aria-controls="pills-home"
                      aria-selected="true"
                    >
                      <MdOutlineEventNote />
                      Overview
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link rounded"
                      id="pills-profile-tab"
                      data-bs-toggle="pill"
                      data-bs-target="#pills-profile"
                      type="button"
                      role="tab"
                      aria-controls="pills-profile"
                      aria-selected="false"
                    >
                      <BsFillLampFill />
                      Amenities
                    </button>
                  </li>
                  <li class="nav-item" role="presentation">
                    <button
                      class="nav-link rounded"
                      id="pills-details-tab"
                      data-bs-toggle="pill"
                      data-bs-target="#pills-details"
                      type="button"
                      role="tab"
                      aria-controls="pills-details"
                      aria-selected="false"
                    >
                      <BiDetail />
                      Full Details
                    </button>
                  </li>
                </ul>
                <div class="tab-content " id="pills-tabContent">
                  <div
                    class="tab-pane fade show active"
                    id="pills-home"
                    role="tabpanel"
                    aria-labelledby="pills-home-tab"
                  >
                    <div className="px-3">
                      <div className="my-1 mb-2 d-flex">
                        <span className="border-primary-color rounded-pill p-1 px-3 fs-8">
                          {item?.listingPropertyType}
                        </span>

                        <span className="border-primary-color rounded-pill p-1 px-3 fs-8 ms-2">
                          {item?.listingType}
                        </span>
                      </div>

                      <h6 class="text-secondary fw-bold">
                        {item?.listingAddress}
                      </h6>
                      <p className="text-primary-color fs-9 fw-bold mb-2">
                        ${item?.listingRent}
                      </p>
                      <p className=" fs-8 text-secondary fw-bold d-flex align-items-center">
                        <span>
                          {" "}
                          <FaLocationDot />
                        </span>
                        <span>{item?.listingMinorRegion}</span>,
                        <span>{item?.listingMajorRegion}</span>
                      </p>
                      <p className=" fs-8 text-secondary">
                        <span>
                          {item?.bedroomCount && parseInt(item?.bedroomCount)}{" "}
                          Bed
                        </span>{" "}
                        |
                        <span>
                          {item?.bathroomCount && parseInt(item?.bathroomCount)}{" "}
                          Bath
                        </span>{" "}
                        |<span> {item?.listingSizeSquareFeet} SF </span>
                      </p>

                      <div className="d-flex justify-content-between align-items-center mx-auto">
                        {getAllScores("walking", item?.walkScore)}
                        {getAllScores("bike", item?.bikeScore)}
                        {getAllScores("transit", item?.transitScore)}
                      </div>
                    </div>
                  </div>
                  <div
                    class="tab-pane fade "
                    id="pills-profile"
                    role="tabpanel"
                    aria-labelledby="pills-profile-tab"
                  >
                    <div className=" px-3">
                      {getAllperks("Amenity")}
                      {getAllperks("Utility")}
                      {getAllperks("Policy")}
                      <p className="fs-9 mt-3 mb-4">
                        <span className="text-primary-color">Note:</span> Only
                        those amenities/utilities/policy that are available is
                        shown.
                      </p>
                    </div>
                  </div>
                  <div
                    class="tab-pane fade p-2"
                    id="pills-details"
                    role="tabpanel"
                    aria-labelledby="pills-details-tab"
                  >
                    <div className="d-flex justify-content-between align-items-center flex-wrap w-75 mx-auto">
                      {getAllScores("grocery", item?.retailGroceryScore)}
                      {getAllScores("Recreation", item?.retailRecreationScore)}
                      {getAllScores("education", item?.educationCenterScore)}
                      {getAllScores("emergency", item?.emergencyCenterScore)}
                      {getAllScores("crime", item?.crimeScore)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="row"></div>
      </div>
    </>
  );
};

export default SingleView;
