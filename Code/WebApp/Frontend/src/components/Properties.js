import React, { useEffect, useState } from "react";
import Filter from "./Filter";
import Search from "./Search";
import Listing from "./Listing";
import Dropdown from "../common/Dropdown";
import { MdClose } from "react-icons/md";
import { instance } from "../config/config";
import Loading from "./Loading";

const Properties = () => {
  // const initialData = jsonData;
  const [initialData, setInitialData] = useState([]);
  const [data, setData] = useState(initialData);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState({});
  const [sortBy, setSortBy] = useState(""); // State for sorting
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);

  useEffect(() => {
    setDataLoading(true);
    instance
      .get("api/listings")
      .then((res) => {
        setDataLoading(false);
        setInitialData(res?.data);
      })
      .catch((err) => {
        setDataLoading(false);
        setMessage("Sorry, no listing found");
        console.log(err);
      });
  }, []);

  useEffect(() => {
    setData(initialData);
  }, [initialData]);

  useEffect(() => {
    // Apply search
    const searchResult = initialData?.filter((item) =>
      item?.listingAddress?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setData(searchTerm ? searchResult : initialData);
  }, [searchTerm]);

  useEffect(() => {
    setLoading(true);
    filters && Object.keys(filters)?.length > 0
      ? instance
          .post("api/listings/filter", filters)
          .then((res) => {
            setFilteredData(res?.data);
            // console.log(res);
            setLoading(false);
          })
          .catch((err) => {
            setLoading(false);
            console.log(err);
          })
      : setFilteredData(data);
  }, [filters, data, sortBy]);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilter = (selectedFilter) => {
    setFilters((filters) => ({
      ...selectedFilter,
      listingRent: {
        // Spread the existing listingRent object
        ...filters?.listingRent,
        // If minVal input is empty, set it to 0 or keep the existing value
        minVal: selectedFilter?.listingRent?.minVal || 0,
        // If maxVal input is empty, set it to 30000 or keep the existing value
        maxVal: selectedFilter?.listingRent?.maxVal || 3000,
      },
    }));
  };

  const clearAll = () => {
    setSearchTerm("");
    setFilters({});
    setData(initialData);
  };

  const removeItem = (item) => {
    setFilters((prevData) => {
      // Create a copy of the state object
      const newData = { ...prevData };
      // Remove the property
      delete newData[item];
      // Return the updated state object
      return newData;
    });
  };
  return (
    <>
      <div className="container py-4">
        <div className=" custom-bottom">
          <div className=" d-flex justify-content-between align-items-center w-100 py-4">
            <Search searchTerm={searchTerm} handleSearch={handleSearch} />

            <div className="d-flex">
              <button
                className=" px-2 py-2 bg-primary-color border-0  ms-2 fs-9"
                type="button"
                data-bs-toggle="offcanvas"
                data-bs-target="#offcanvasRight"
                aria-controls="offcanvasRight"
              >
                More Filter
              </button>

              <div
                class="offcanvas offcanvas-end"
                tabindex="-1"
                id="offcanvasRight"
                aria-labelledby="offcanvasRightLabel"
              >
                <div class="offcanvas-header px-4 custom-bottom">
                  <h5 id="offcanvasRightLabel">Filter By</h5>
                  <button
                    type="button"
                    class="btn-close text-reset"
                    data-bs-dismiss="offcanvas"
                    aria-label="Close"
                  ></button>
                </div>
                <div class="offcanvas-body py-4">
                  {" "}
                  <Filter
                    handleFilter={handleFilter}
                    clearAll={clearAll}
                    allData={data}
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="my-2 filtersBadge">
            {filters &&
              Object?.keys(filters)?.map((item, idx) => {
                // console.log(filters[item]);
                return (
                  <span className="badge rounded-pill bg-primary-color text-capitalize me-2">
                    {typeof filters[item] !== "object" ? (
                      <>
                        <span>{item?.replace(/_/g, " ")} :</span>
                        <span> {filters[item]}</span>
                      </>
                    ) : (
                      <>
                        <span>{item?.replace(/_/g, " ")} :</span>
                        <span>
                          {" "}
                          {filters[item]?.minVal} - {filters[item]?.maxVal}
                        </span>
                      </>
                    )}
                    <MdClose
                      className="icon"
                      onClick={() => removeItem(item)}
                    />
                  </span>
                );
              })}

            {!loading && filteredData?.length == 0 && (
              <p className="fs-9 mb-0 pt-3">Sorry, no listing found</p>
            )}
          </div>
        </div>
      </div>
      {!dataLoading ? (
        <Listing filteredItems={filteredData} message={message} />
      ) : (
        <div className="w-100 h-100 d-flex justify-content-center align-items-center">
          <Loading />
        </div>
      )}
    </>
  );
};

export default Properties;
