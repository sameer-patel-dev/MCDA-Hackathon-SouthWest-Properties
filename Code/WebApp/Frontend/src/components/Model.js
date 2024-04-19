import React, { useEffect, useRef, useState } from "react";
import Dropdown from "../common/Dropdown";
import Switch from "react-switch";
import { AddressAutofill } from "@mapbox/search-js-react";
import Address from "./Address";
import Button from "../common/Button";
import { FaFileCsv } from "react-icons/fa";
import Papa from "papaparse";
import MultiStep from "react-multistep";
import { instance } from "../config/config";
import Message from "../common/Message";
import { setSelectionRange } from "@testing-library/user-event/dist/utils";
import { useNavigate, useLocation } from "react-router-dom";
import Loading from "./Loading";
import ModelTrainingState from "./ModelTrainingState";

const Model = () => {
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [columnNames, setColumnNames] = useState([]);
  const [fileState, setFileState] = useState({
    succces: null,
    message: "",
  });
  const [succcesMessage, setSuccessMessage] = useState(null);
  const [modelLoading, setModalLoading] = useState(false);
  const [loading, setLoading] = useState(false);

  const [sampleData] = useState({
    expectedColumns: [
      "listingAddress",
      "listingPropertyType",
      "listingSizeSquareFeet",
      "bedroomCount",
      "bathroomCount",
      "heatUtility",
      "waterUtility",
      "hydroUtility",
      "furnishedUtility",
      "petPolicy",
      "smokingPolicy",
      "gymAmenity",
      "parkingAmenity",
      "acAmenity",
      "applianceAmenity",
      "storageAmenity",
    ],
    expectedRows: [
      '"106 Dalkeith Drive, Dartmouth, Nova Scotia, B2W 4E8"',
      "TownHouse",
      "1558.0",
      "4.0",
      "2.0",
      "0",
      "1",
      "0",
      "0",
      "0.0",
      "0",
      "0",
      "0",
      "0",
      "0",
      "0",
    ],
  });

  const [data, setData] = useState({
    propertyType: ["TownHouse", "Apartment"],
    bedroom: [1, 2, 3, 4],
    bath: [1, 2, 3, 4],
    utility: [],
    policies: [],
    amenities: [],
    address: "",
    sqFt: 0,
  });

  const [selectedFeature, setSelectedFeature] = useState({
    listingAddress: "",
    listingPropertyType: "",
    listingSizeSquareFeet: "",
    bedroomCount: "",
    bathroomCount: "",
    heatUtility: 0,
    waterUtility: 0,
    hydroUtility: 0,
    furnishedUtility: 0,
    petPolicy: 0,
    smokingPolicy: 0,
    gymAmenity: 0,
    parkingAmenity: 0,
    acAmenity: 0,
    applianceAmenity: 0,
    storageAmenity: 0,
  });

  const steps = [
    {
      title: "Basic Info",
      component: (
        <Basic
          data={data}
          setData={setData}
          selectedFeature={selectedFeature}
          setSelectedFeature={setSelectedFeature}
        />
      ),
    },
    {
      title: "Utilities",
      component: (
        <Utilities
          data={data}
          setData={setData}
          selectedFeature={selectedFeature}
          setSelectedFeature={setSelectedFeature}
        />
      ),
    },
    {
      title: "Policy",
      component: (
        <Policy
          data={data}
          setData={setData}
          selectedFeature={selectedFeature}
          setSelectedFeature={setSelectedFeature}
        />
      ),
    },
    {
      title: "Amenities",
      component: (
        <Amenity
          data={data}
          setData={setData}
          selectedFeature={selectedFeature}
          setSelectedFeature={setSelectedFeature}
        />
      ),
    },
  ];

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      const fileNameParts = selectedFile.name.split(".");
      const fileExtension = fileNameParts[fileNameParts.length - 1];
      if (fileExtension !== "csv") {
        setErrorMessage("You can only upload a CSV file.");
        return;
      } else {
        validateCSVColumns(selectedFile);
        if (selectedFile) {
          const currentDate = new Date().toISOString()?.replace(/[-:.]/g, "");
          const newName = `${selectedFile.name
            ?.split(".")
            ?.slice(0, -1)
            ?.join(".")}_${currentDate}.${selectedFile.name.split(".")?.pop()}`;
          const renamedFile = new File([selectedFile], newName, {
            type: selectedFile.type,
          });

          setFile(renamedFile);
        }
        // setFile(selectedFile);
      }
    }
  };

  const validateCSVColumns = (selectedFile) => {
    Papa.parse(selectedFile, {
      header: true,
      complete: (results) => {
        if (
          results &&
          results?.meta?.fields &&
          results?.meta?.fields?.length > 0
        ) {
          // const columnsToBeIncluded = [];
          results?.meta?.fields?.map((field, idx) => {
            if (!columnNames?.includes(field[idx])) {
              setColumnNames(results?.meta?.fields);
            }
          });
        }
      },
      error: (error) => {
        setErrorMessage("Error parsing the CSV file.");
      },
    });
  };

  useEffect(() => {
    if (file !== null) {
      if (columnNames?.length === 0) {
        return setErrorMessage("No CSV header detected.");
      }

      const missingColumns = sampleData?.expectedColumns.filter(
        (column) => !columnNames.includes(column)
      );
      if (missingColumns.length === 0) {
        return setErrorMessage("");
      } else {
        return setErrorMessage(
          `Some necessary columns are missing. Please Look at the Sample CSV.`
        );
      }
    }
  }, [columnNames]);

  const onSubmit = async (e) => {
    e?.preventDefault();
    if (!errorMessage) {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await instance.post("/api/csv_upload", formData);

        if (response) {
          setFileState({
            succces: true,
            message: response?.message,
          });
          setLoading(false);
        }
      } catch (error) {
        setFileState({
          succces: false,
          message:
            "Something went wrong. Could not upload the file, please try again later",
        });

        setLoading(false);
      }
    }
  };

  const navigate = useNavigate();

  const [showPrediction, setShowPrediction] = useState(false);
  const onSingleModelSubmit = (e) => {
    e.preventDefault();
    setModalLoading(true);

    instance.defaults.timeout = 700000;

    instance
      .post("/api/rent-forecast", selectedFeature)
      .then((response) => {
        if (response) {
          setModalLoading(false);

          navigate("/prediction/status", {
            state: {
              state: modelLoading,
              message: response?.data,
              feature: selectedFeature,
            },
          });
        }
        setErrorMessage("");
      })
      .catch((err) => {
        setModalLoading(false);
        console.log(err);
        setErrorMessage("Something went wrong. Could not predict the rent.");
      });
  };

  const downloadSampleCSV = () => {
    const { expectedColumns, expectedRows } = sampleData;

    // Convert to CSV format
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [expectedColumns?.join(","), expectedRows?.join(",")]?.join("\n");

    // Create a link element and trigger download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "sampleModelData.csv");
    document.body.appendChild(link);
    link.click();
  };

  return (
    <>
      {modelLoading ? (
        <ModelTrainingState state={modelLoading} message={""} />
      ) : (
        !showPrediction &&
        (fileState?.succces ? (
          <Message message={fileState?.message} />
        ) : (
          <div className="landingPage my-5">
            <div className="header text-center mb-4">
              <h2 className="mb-1">Find the ideal rent price</h2>
            </div>
            <div class="container-fluid text-center">
              <div class="row justify-content-center">
                <div class="col-lg-12 col-md-12 col-sm-12 ">
                  <span className="secondaryHead text-left text-muted ">
                    Upload a CSV with necessary columns
                  </span>{" "}
                  <div className="mt-4">
                    <p class="border-0 bg-transparent mt-3 cursor-pointer">
                      <span className="text-primary-color">Note:</span>
                      <span className="fs-9">
                        {" "}
                        Please look at the{" "}
                        <span
                          className="text-decoration-underline fs-9 text-primary-color text-uppercase"
                          onClick={downloadSampleCSV}
                        >
                          sample CSV
                        </span>{" "}
                        to know which format to upload the file
                      </span>{" "}
                    </p>
                    <div class="mb-3 mt-2 w-50 mx-auto">
                      <input
                        class="form-control"
                        type="file"
                        id="formFile"
                        onChange={handleFileChange}
                        accept=".csv"
                      />
                      {file && !errorMessage && (
                        <p className="text-primary-color py-3">
                          {" "}
                          <FaFileCsv />
                          {file?.name}
                        </p>
                      )}
                      {!fileState?.succces && (
                        <p className="text-danger fs-9 mt-3">
                          {fileState?.message}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="footer">
                    {loading ? <Loading /> : ""}
                    <Button
                      onClick={onSubmit}
                      className=" px-2 py-2 bg-primary-color border-0 rounded-0  ms-2 fs-9"
                      disabled={
                        errorMessage !== "" || file === null || loading
                          ? true
                          : false
                      }
                    >
                      Predict
                    </Button>
                    {fileState?.message && <p>{fileState?.message}</p>}
                  </div>
                </div>
                <div className="my-4 custom-bottom">{/* <p>OR</p> */}</div>

                <div className="col-lg-12 col-md-12 col-sm-12 mt-4">
                  <span className="secondaryHead text-left text-muted ">
                    Predict the rent for a single location
                  </span>{" "}
                  {errorMessage && (
                    <p className="text-danger fs-9 mt-3">{errorMessage}</p>
                  )}
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
                      nextButton={{
                        title: "Next",
                        style: {
                          background: "transparent",
                          border: "1px solid #c1cd23",
                          color: "#c1cd23",
                          padding: ".2em 1.2em",
                          margin: "2em 1em",
                        },
                      }}
                    />
                  </div>
                  <Button
                    onClick={onSingleModelSubmit}
                    className=" px-2 py-2 bg-primary-color border-0 rounded-0  ms-2 fs-9 my-3"
                    disabled={errorMessage !== "" || loading ? true : false}
                  >
                    Predict
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </>
  );
};

export const Basic = ({
  data,
  setData,
  selectedFeature,
  setSelectedFeature,
}) => {
  const addressChange = (e) => {
    setData((data) => ({ ...data, address: e?.target?.value }));
  };

  const handleRetrieve = (feature) => {
    setData((data) => ({
      ...data,
      address: feature?.features[0]?.properties?.full_address,
    }));
    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      listingAddress: feature?.features[0]?.properties?.full_address,
    }));
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center">
        <Dropdown
          // className={"border-bottom"}
          options={data?.propertyType}
          title="Property Type"
          name="listingPropertyType"
          value={selectedFeature?.listingPropertyType || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              listingPropertyType: e?.target?.value,
            }))
          }
        />
        <Dropdown
          className={"mx-2"}
          options={data?.bedroom}
          title="Bedroom"
          name="bedroomCount"
          value={selectedFeature?.bedroomCount || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              bedroomCount: e?.target?.value,
            }))
          }
        />
        <Dropdown
          options={data?.bath}
          title="Baths"
          name="bathroomCount"
          value={selectedFeature?.bathroomCount || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              bathroomCount: e?.target?.value,
            }))
          }
        />
      </div>
      <div>
        <div className="my-4 custom-border d-flex justify-content-between">
          <div className="w-75 autocomplete-address">
            <AddressAutofill
              onRetrieve={handleRetrieve}
              accessToken={"pk.eyJ1Ijoia3JpdGlrYWtvaXJhbGEiLCJhIjoiY2x0enhmaWRmMDU1eTJrb21hYXliN3ZyOSJ9.QZJhgU5tMeANennF48VcpA"}
            >
              <input
                className="form-control border-0 border-bottom rounded-0 fs-8 py-1 px-0 w-100 "
                name="address"
                placeholder="Type your postal address like 5672 Cornel st...."
                type="text"
                autoComplete="address-line1"
                onChange={addressChange}
                value={data?.address}
              />
            </AddressAutofill>
          </div>
        </div>

        <input
          className="form-control w-25"
          placeholder="Listing Sq ft"
          type="number"
          name="listingSizeSquareFeet"
          value={selectedFeature?.listingSizeSquareFeet || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              listingSizeSquareFeet: e?.target?.value,
            }))
          }
        />
      </div>
    </>
  );
};

export const Utilities = ({ selectedFeature, setSelectedFeature }) => {
  const allUtilities = [
    "heatUtility",
    "waterUtility",
    "hydroUtility",
    "furnishedUtility",
  ];

  const utilityChange = (e) => {
    const { name, value, checked } = e?.target;
    // console.log(data);

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? 1 : 0,
    }));
  };

  return (
    <div className="d-flex justify-content-center align-items-center flex-wrap">
      {allUtilities?.map((utility, idx) => {
        return (
          <div class="form-check form-check-inline" onChange={utilityChange}>
            <input
              class="form-check-input"
              type="checkbox"
              id={idx}
              value={utility}
              name={utility}
            />
            <label class="form-check-label text-capitalize fs-8" for={idx}>
              {utility?.split("Utility")[0]}
            </label>
          </div>
        );
      })}
    </div>
  );
};

export const Policy = ({ selectedFeature, setSelectedFeature }) => {
  const allPolicies = ["petPolicy", "smokingPolicy"];

  const policyChange = (e) => {
    const { name, value, checked } = e?.target;

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? 1 : 0,
    }));
  };
  return (
    <div className="d-flex justify-content-center align-items-center flex-wrap">
      {allPolicies?.map((policy, idx) => {
        return (
          <div class="form-check form-check-inline" onChange={policyChange}>
            <input
              class="form-check-input"
              type="checkbox"
              id={idx}
              value={policy}
              name={policy}
            />
            <label class="form-check-label text-capitalize fs-8" for={idx}>
              {policy?.split("Policy")[0]}
            </label>
          </div>
        );
      })}
    </div>
  );
};

export const Amenity = ({ selectedFeature, setSelectedFeature }) => {
  const allAmenities = [
    "gymAmenity",
    "parkingAmenity",
    "acAmenity",
    "applianceAmenity",
    "storageAmenity",
  ];

  const onamenityChange = (e) => {
    const { name, value, checked } = e?.target;

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? 1 : 0,
    }));
  };
  return (
    <div className="d-flex justify-content-center align-items-center flex-wrap">
      {" "}
      {allAmenities?.map((amenity, idx) => {
        return (
          <div class="form-check form-check-inline" onChange={onamenityChange}>
            <input
              class="form-check-input"
              type="checkbox"
              id={idx}
              value={amenity}
              name={amenity}
            />
            <label class="form-check-label text-capitalize fs-8" for={idx}>
              {amenity?.split("Amenity")[0]}
            </label>
          </div>
        );
      })}
    </div>
  );
};

// export const ModelTrainingState = () => {
//   const location = useLocation();
//   const { state, message, feature, steps } = location?.state;

//   console.log(state);

//   return (
//     <div className="w-100 bg-white mx-auto vh-70 pt-5 mt-5">
//       {
//         <div>
//           {!state && message?.message !== "" && (
//             <>
//               <div className="d-flex flex-column justify-content-center align-items-center">
//                 <GiTakeMyMoney fontSize={100} />

//                 <p className="fs-9 text-center pt-2 ">
//                   The predicted rent is:{" "}
//                   <span className="text-primary-color">
//                     ${message?.predictedRent}
//                   </span>
//                 </p>
//               </div>

//               {/* <div className="w-75 mx-auto mt-2">
//                 <p className="fs-9 text-center text-primary-color">
//                   The listing for which you wanted to predict the rent
//                 </p>

//                 {feature && Object.keys(feature)?.length > 0 && (
//                   <div className="table-responsive ">
//                     <table className="table table-bordered table-sm fs-9">
//                       <thead>
//                         <tr>
//                           {feature &&
//                             Object.keys(feature)?.map((feat, idx) => {
//                               return (
//                                 <th className="fst-italic fw-normal">{feat}</th>
//                               );
//                             })}
//                         </tr>
//                       </thead>
//                       <tbody>
//                         <tr>
//                           {feature &&
//                             Object.keys(feature)?.map((feat, idx) => {
//                               return (
//                                 <td className="fst-italic fw-normal">
//                                   {feature[feat]}
//                                 </td>
//                               );
//                             })}
//                         </tr>
//                       </tbody>
//                     </table>
//                   </div>
//                 )}
//               </div> */}
//               {/* <div className="shadow px-4 w-50 mx-auto mt-4">
//                 <MultiStep
//                   activeStep={0}
//                   showNavigation={true}
//                   steps={steps}
//                   prevButton={{
//                     title: "Back",
//                     style: {
//                       background: "transparent",
//                       border: "1px solid #c1cd23",
//                       color: "#c1cd23",
//                       padding: ".2em 1.2em",
//                     },
//                   }}
//                   nextButton={{
//                     title: "Next",
//                     style: {
//                       background: "transparent",
//                       border: "1px solid #c1cd23",
//                       color: "#c1cd23",
//                       padding: ".2em 1.2em",
//                       margin: "2em 1em",
//                     },
//                   }}
//                 />
//               </div> */}
//             </>
//           )}
//         </div>
//       }
//     </div>
//   );
// };

export default Model;
