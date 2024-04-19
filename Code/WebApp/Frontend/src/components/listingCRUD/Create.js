import React, { useState, useEffect } from "react";
import { FaFileCsv } from "react-icons/fa";
import Loading from "../Loading";
import Button from "../../common/Button";
import MultiStep from "react-multistep";
import Dropdown from "../../common/Dropdown";
import { AddressAutofill } from "@mapbox/search-js-react";
import { instance } from "../../config/config";
import Papa from "papaparse";

const Create = () => {
  const [file, setFile] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [columnNames, setColumnNames] = useState([]);

  const [successMessage, setSuccessMessage] = useState("");

  const [data, setData] = useState({
    property_type: ["TownHouse", "Apartment"],
    listing_property_type: ["Management", "Rental"],
    bedroom: ["1", "2", "3", "4+"],
    bath: ["1", "2", "3", "4+"],
    utility: [],
    policies: [],
    amenities: [],
    address: "",
    sqFt: 0,
    rent: 0,
    imageLink: "",
  });

  const [selectedFeature, setSelectedFeature] = useState({
    street_address: "",
    property_type: "",
    listing_property_type: "",
    square_feet: 0,
    imageLink: "",
    bedroom: 0,
    bathroom: 0,
    heat: false,
    water: false,
    hydro: false,
    furnished: false,
    pet: false,
    smoking: false,
    gym: false,
    parking: false,
    ac: false,
    appliance: false,
    storage: false,
    rent: 0,
  });

  const [sampleData] = useState({
    expectedColumns: [
      "listingType",
      "listingAddress",
      "listingPropertyType",
      "listingSizeSquareFeet",
      "imageLink",
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
      "listingRent",
    ],

    expectedRows: [
      "townhouse",
      '"106 Dalkeith Drive, Dartmouth, Nova Scotia, B2W 4E8"',
      "TownHouse",
      "2000",
      "https://www.google.com/url?house-image.jpg",
      "1",
      "2",
      "true",
      "true",
      "false",
      "true",
      "true",
      "true",
      "false",
      "true",
      "true",
      "true",
      "false",
      "2000",
    ],
  });

  const [fileState, setFileState] = useState({
    succces: null,
    message: "",
  });

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      const fileNameParts = selectedFile.name.split(".");
      const fileExtension = fileNameParts[fileNameParts.length - 1];
      if (fileExtension !== "csv") {
        setFileState({
          succces: false,
          message: "You can only upload a CSV file.",
        });
        // setErrorMessage("You can only upload a CSV file.");
        return;
      } else {
        validateCSVColumns(selectedFile);

        setFile(selectedFile);
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
        setFileState({
          succces: false,
          message: "Error parsing the CSV file.",
        });
      },
    });
  };

  useEffect(() => {
    if (file !== null) {
      if (columnNames?.length === 0) {
        return setFileState({
          succces: false,
          message: "No CSV header detected.",
        });
      }
      const missingColumns = sampleData?.expectedColumns.filter(
        (column) => !columnNames.includes(column)
      );

      if (missingColumns.length === 0) {
        return setFileState({
          succces: false,
          message: "",
        });
      } else {
        return setFileState({
          succces: false,
          message:
            "Some necessary columns are missing. Please Look at the Sample CSV.",
        });
      }
    }
  }, [columnNames]);

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

  const onSubmit = async (e) => {
    e?.preventDefault();
    if (!errorMessage) {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      try {
        const response = await instance.post("/api/csv_import", formData);
        if (response) {
          setFileState({
            succces: true,
            message: "File uploaded Successfully!",
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

  const onSingleModelSubmit = (e) => {
    e.preventDefault();
    setErrorMessage("");
    setLoading(true);

    instance
      .post("/api/listings", selectedFeature, { timeout: 600000 })
      .then((res) => {
        setLoading(false);
        setSuccessMessage("Listing Added successfully!");
      })
      .catch((err) => {
        setLoading(false);
        setErrorMessage("Something went wrong. We couldn't add the listing.");
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
    link.setAttribute("download", "sampleListingData.csv");
    document.body.appendChild(link);
    link.click();
  };

  return (
    <>
      <div className="w-50 mx-auto m-4 shadow">
        <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
          <li class="nav-item" role="presentation">
            <button
              class="nav-link active"
              id="pills-home-tab"
              data-bs-toggle="pill"
              data-bs-target="#pills-home"
              type="button"
              role="tab"
              aria-controls="pills-home"
              aria-selected="true"
            >
              File Upload
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              id="pills-profile-tab"
              data-bs-toggle="pill"
              data-bs-target="#pills-profile"
              type="button"
              role="tab"
              aria-controls="pills-profile"
              aria-selected="false"
            >
              Manual Entry
            </button>
          </li>
        </ul>
        <div class="tab-content py-3" id="pills-tabContent">
          <div
            class="tab-pane fade show active"
            id="pills-home"
            role="tabpanel"
            aria-labelledby="pills-home-tab"
          >
            <div className="w-75 mx-auto">
              {
                <p
                  className={`fs-9 ${
                    fileState?.succces === true ? "text-success" : "text-danger"
                  }`}
                >
                  {fileState?.message}
                </p>
              }
              <p
                class="border-0 bg-transparent cursor-pointer"
                // data-bs-toggle="modal"
                // data-bs-target="#exampleModal"
              >
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
              <div>
                <input
                  class="form-control"
                  type="file"
                  id="formFile"
                  onChange={handleFileChange}
                  accept=".csv"
                />

                {file && (
                  <p className="text-primary-color py-3">
                    {" "}
                    <FaFileCsv />
                    {file?.name}
                  </p>
                )}
              </div>

              <div className="footer d-flex justify-content-center my-3">
                {loading ? <Loading /> : ""}
                <Button
                  onClick={onSubmit}
                  className=" px-2 py-2 bg-primary-color border-0 rounded-0  ms-2 fs-9"
                  disabled={
                    fileState?.message !== "" || file === null || loading
                      ? true
                      : false
                  }
                >
                  Add
                </Button>
              </div>
            </div>
          </div>
          <div
            class="tab-pane fade"
            id="pills-profile"
            role="tabpanel"
            aria-labelledby="pills-profile-tab"
          >
            {errorMessage && (
              <p className="text-danger fs-9 mt-3 text-center">
                {errorMessage}
              </p>
            )}

            {successMessage && (
              <p className="text-success fs-9 mt-3 text-center">
                {successMessage}
              </p>
            )}

            <div className=" px-4 mx-auto">
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
                    margin: "2em 1em 0 1em",
                  },
                }}
              />
            </div>
            <div className="d-flex justify-content-center align-items-center">
              {loading ? <Loading /> : ""}
              <Button
                onClick={onSingleModelSubmit}
                className="justify-content-center px-2 py-2 bg-primary-color border-0 rounded-0  ms-2 fs-9 my-3"
                disabled={loading || successMessage !== "" ? true : false}
              >
                Add
              </Button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Create;

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
      street_address: feature?.features[0]?.properties?.full_address,
    }));
  };

  return (
    <>
      <div className="d-flex justify-content-between align-items-center">
        <Dropdown
          className={"me-2"}
          options={data?.property_type}
          title="Property Type"
          name="property_type"
          value={selectedFeature?.property_type || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              property_type: e?.target?.value,
            }))
          }
        />
        <Dropdown
          // className={"mx-2"}
          options={data?.listing_property_type}
          title="Listing Property Type"
          name="listing_property_type"
          value={selectedFeature?.listing_property_type || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              listing_property_type: e?.target?.value,
            }))
          }
        />
      </div>
      <div className="d-flex justify-content-between align-items-center mt-2">
        <Dropdown
          className={"me-2"}
          options={data?.bedroom}
          title="Bedroom"
          name="bedroom"
          value={selectedFeature?.bedroom || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              bedroom: parseInt(e?.target?.value),
            }))
          }
        />
        <Dropdown
          options={data?.bath}
          title="Baths"
          name="bathroom"
          value={selectedFeature?.bathroom || ""}
          onChange={(e) =>
            setSelectedFeature((selectedFeature) => ({
              ...selectedFeature,
              bathroom: parseInt(e?.target?.value),
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
        <div className="d-flex justify-content-between align-items-center">
          <input
            className="form-control"
            placeholder="Listing Sq ft"
            type="number"
            name="square_feet"
            value={selectedFeature?.square_feet || ""}
            onChange={(e) =>
              setSelectedFeature((selectedFeature) => ({
                ...selectedFeature,
                square_feet: parseInt(e?.target?.value),
              }))
            }
          />
          <input
            className="form-control mx-2"
            placeholder="Rent"
            type="number"
            name="rent"
            value={selectedFeature?.rent || ""}
            onChange={(e) =>
              setSelectedFeature((selectedFeature) => ({
                ...selectedFeature,
                rent: parseInt(e?.target?.value),
              }))
            }
          />

          <input
            className="form-control "
            placeholder="Image Link"
            type="text"
            name="imageLink"
            value={selectedFeature?.imageLink || ""}
            onChange={(e) =>
              setSelectedFeature((selectedFeature) => ({
                ...selectedFeature,
                imageLink: e?.target?.value,
              }))
            }
          />
        </div>
      </div>
    </>
  );
};
export const Utilities = ({ selectedFeature, setSelectedFeature }) => {
  const allUtilities = ["heat", "water", "hydro", "furnished"];

  const utilityChange = (e) => {
    const { name, value, checked } = e?.target;
    // console.log(data);

    console.log(checked ? true : false);

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? true : false,
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
              {utility}
            </label>
          </div>
        );
      })}
    </div>
  );
};
export const Policy = ({ selectedFeature, setSelectedFeature }) => {
  const allPolicies = ["pet", "smoking"];

  const policyChange = (e) => {
    const { name, value, checked } = e?.target;

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? true : false,
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
              {policy}
            </label>
          </div>
        );
      })}
    </div>
  );
};
export const Amenity = ({ selectedFeature, setSelectedFeature }) => {
  const allAmenities = ["gym", "parking", "ac", "appliance", "storage"];

  const onamenityChange = (e) => {
    const { name, value, checked } = e?.target;

    setSelectedFeature((selectedFeature) => ({
      ...selectedFeature,
      [value]: checked ? true : false,
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
              {amenity}
            </label>
          </div>
        );
      })}
    </div>
  );
};
