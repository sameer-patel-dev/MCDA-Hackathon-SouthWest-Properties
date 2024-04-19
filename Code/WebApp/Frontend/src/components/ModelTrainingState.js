import React, { useEffect, useState } from "react";
import { GiTakeMyMoney } from "react-icons/gi";
import MultiStep from "react-multistep";
import { useLocation } from "react-router-dom";

const ModelTrainingState = ({ state, message }) => {
  const location = useLocation();
  const [response, setResponse] = useState({
    state: null,
    message: "",
  });
  //   let feature = {};
  const [feature, setFeature] = useState({});
  //   console.log(state);
  //   console.log(message);

  useEffect(() => {
    if (location !== null) {
      setFeature(location?.state?.feature);
      setResponse({
        state: location?.state?.state,
        message: location?.state?.message,
      });
    }
  }, [location]);

  const responseSteps = [
    "Calculating Transit Score",
    "Calculating Walk Score",
    "Calculating Bike Score",
    "Calculating Crime Score",
    "Calculating Grocery Score",
    "Calculating Recreation Score",
    "Calculating Education Score",
    "Calculating Emergency Score",
    "Please wait while we provide you with the predicted rent.",
  ];

  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      if (currentStep < responseSteps.length - 1) {
        return setCurrentStep((prevStep) => prevStep + 1);
      } else {
        clearInterval(interval);
      }
    }, 5000); // Show each step for 5 seconds

    // Clear the interval after 40 seconds
    const timeout = setTimeout(() => {
      clearInterval(interval);
    }, 35000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [currentStep, responseSteps.length]);

  const progress = ((currentStep + 1) / responseSteps.length) * 100;

  const BasicInfo = () => (
    <div>
      <div className="d-flex justify-content-between align-items-center">
        <input
          className={"form-control"}
          placeholder="Property Type"
          name="listingPropertyType"
          value={"Property Type: " + feature?.listingPropertyType || ""}
          disabled={true}
        />
        <input
          className={"mx-2 form-control"}
          placeholder="Bedroom"
          name="bedroomCount"
          value={"Bedroom: " + feature?.bedroomCount || ""}
          disabled={true}
        />
        <input
          className={"form-control"}
          placeholder="Baths"
          name="bathroomCount"
          value={"Bath: " + feature?.bathroomCount || ""}
          disabled={true}
        />
      </div>
      <div>
        <div className="my-4 custom-border d-flex justify-content-between">
          <input
            className={"form-control"}
            placeholder="Address"
            name="listingAddress"
            value={"Address: " + feature?.listingAddress || ""}
            disabled={true}
          />
        </div>
        {console.log(feature)}
        <input
          className="form-control w-50"
          placeholder="Listing Sq ft"
          name="listingSizeSquareFeet"
          value={"Sq Ft: " + feature?.listingSizeSquareFeet || ""}
          disabled={true}
        />
      </div>
    </div>
  );

  const allUtilities = [
    "heatUtility",
    "waterUtility",
    "hydroUtility",
    "furnishedUtility",
  ];
  const Utilities = () => (
    <div className="d-flex justify-content-center align-items-center flex-wrap">
      {allUtilities?.map((util, idx) => {
        return (
          <div class="form-check form-check-inline" key={idx}>
            <input
              class="form-check-input"
              type="checkbox"
              id={idx}
              value={util}
              name={util}
              checked={feature && feature[util] === 1}
              disabled
            />
            <label class="form-check-label text-capitalize fs-8" for={idx}>
              {util?.split("Utility")[0]}
            </label>
          </div>
        );
      })}
    </div>
  );
  const allPolicies = ["petPolicy", "smokingPolicy"];

  const Policy = () => (
    <>
      {" "}
      <div className="d-flex justify-content-center align-items-center flex-wrap">
        {allPolicies?.map((util, idx) => {
          return (
            <div class="form-check form-check-inline" key={idx}>
              <input
                class="form-check-input"
                type="checkbox"
                id={idx}
                value={util}
                name={util}
                checked={feature && feature[util] === 1}
                disabled
              />
              <label class="form-check-label text-capitalize fs-8" for={idx}>
                {util?.split("Policy")[0]}
              </label>
            </div>
          );
        })}
      </div>
    </>
  );
  const allAmenities = [
    "gymAmenity",
    "parkingAmenity",
    "acAmenity",
    "applianceAmenity",
    "storageAmenity",
  ];
  const Amenity = () => (
    <>
      <div className="d-flex justify-content-center align-items-center flex-wrap">
        {allAmenities?.map((util, idx) => {
          return (
            <div class="form-check form-check-inline" key={idx}>
              <input
                class="form-check-input"
                type="checkbox"
                id={idx}
                value={util}
                name={util}
                checked={feature && feature[util] === 1}
                disabled
              />
              <label class="form-check-label text-capitalize fs-8" for={idx}>
                {util?.split("Amenity")[0]}
              </label>
            </div>
          );
        })}
      </div>
    </>
  );

  const steps = [
    {
      title: "Basic Info",
      component: BasicInfo(),
    },
    {
      title: "Utilities",
      component: Utilities(),
    },
    {
      title: "Policy",
      component: Policy(),
    },
    {
      title: "Amenities",
      component: Amenity(),
    },
  ];

  return (
    <div className="w-100 bg-white mx-auto vh-70 my-5">
      {state ? (
        <div className="d-flex flex-column justify-content-center align-items-center pt-5 mt-5">
          <div className="d-flex flex-column justify-content-center align-items-center">
            {/* {progress} */}
            <div className="progress" style={{ width: `100%` }}>
              <div
                className="progress-bar progress-bar-striped bg-success progress-bar-animated"
                role="progressbar"
                aria-valuenow={`${progress}`}
                aria-valuemin="0"
                aria-valuemax="100"
                style={{ width: `${progress}%` }}
              ></div>
            </div>

            <p className="mt-3 fs-9">{responseSteps[currentStep]}</p>
          </div>
        </div>
      ) : (
        <div>
          {response?.message?.message !== "" && (
            <>
              <div className="d-flex flex-column justify-content-center align-items-center">
                <GiTakeMyMoney fontSize={100} />

                <p className="fs-9 text-center pt-2 ">
                  The predicted rent is:{" "}
                  <span className="text-primary-color">
                    ${response?.message?.predictedRent}
                  </span>
                </p>
              </div>
              <div className="shadow px-4 w-50 mx-auto mt-4">
                <MultiStep
                  activeStep={0}
                  showNavigation={true}
                  steps={steps}
                  prevButton={{
                    title: "Back",
                    style: {
                      background: "transparent",
                      border: "1px solid #c1cd23",
                      color: "#c1cd23",
                      padding: ".2em 1.2em",
                    },
                  }}
                  nextButton={
                    // Conditionally render next button based on current step
                    {
                      title: "Next",
                      style: {
                        background: "transparent",
                        border: "1px solid #c1cd23",
                        color: "#c1cd23",
                        padding: ".2em 1.2em",
                        margin: "2em 1em",
                      },
                    }
                  }
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ModelTrainingState;
