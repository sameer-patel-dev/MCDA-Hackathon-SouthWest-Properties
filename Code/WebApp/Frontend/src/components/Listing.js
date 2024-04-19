import React, { useEffect, useState } from "react";
import { useFetcher, useNavigate } from "react-router-dom";
import ReactPaginate from "react-paginate";
import Switch from "react-switch";
import { GrFormPrevious, GrFormNext } from "react-icons/gr";
import MapView from "./MapView";
import MiniListing from "./MiniListing";
import Button from "../common/Button";
import noImg from "../assets/img/no-img.jpg";
import Loading from "../components/Loading";

const Listing = ({ filteredItems }) => {
  const [itemToshow, setItemToshow] = useState({});
  const [viewMode, setViewMode] = useState({
    mode: "list",
    checked: true,
  });

  const handleChange = (e) => {
    setViewMode({
      mode: !viewMode?.checked ? "list" : "map",
      checked: !viewMode?.checked,
    });
  };

  const handleMouseEvent = (item) => {
    setItemToshow(item);
  };

  const navigate = useNavigate();

  return (
    <>
      <div className="container">
        <div className="row">
          <div className="col-lg-12 col-md-12 col-sm-12">
            <div className="d-flex justify-content-between align-items-center pb-4 mx-1 mx-auto">
              <div
                className="text-decoration-underline cursor-pointer"
                onClick={(e) => navigate("/listings/create")}
              >
                Add your own Listing?
              </div>
              <div className="toggle d-flex justify-content-center align-items-center">
                <span
                  className={`fs-8 ${
                    viewMode?.mode === "map"
                      ? "text-primary-color"
                      : "text-muted"
                  }`}
                >
                  Map View
                </span>
                <Switch
                  onChange={handleChange}
                  checked={viewMode?.checked}
                  checkedIcon={false}
                  uncheckedIcon={false}
                  className="mx-2"
                  width={52}
                  height={20}
                />
                <span
                  className={`fs-8 ${
                    viewMode?.mode === "list"
                      ? "text-primary-color"
                      : "text-muted"
                  }`}
                >
                  List View
                </span>
              </div>
            </div>
            {viewMode?.mode === "list" ? (
              <PaginatedItems itemsPerPage={8} filteredItems={filteredItems} />
            ) : (
              <div className="container-fluid p-0 ">
                <div className="row">
                  <div className="col-lg-3 col-md-4 col-sm-4 p-0">
                    <MiniListing
                      filteredItems={filteredItems}
                      handleMouseEvent={handleMouseEvent}
                    />
                  </div>
                  <div className="col-lg-8 col-md-8 col-sm-8 pt-2">
                    <MapView
                      filteredItems={filteredItems}
                      itemToshow={itemToshow}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Listing;

export function PaginatedItems({ itemsPerPage, filteredItems }) {
  // Here we use item offsets; we could also use page offsets
  // following the API or data you're working with.
  const [itemOffset, setItemOffset] = useState(0);

  // Simulate fetching items from another resources.
  // (This could be items from props; or items loaded in a local state
  // from an API endpoint with useEffect and useState)

  const endOffset = itemOffset + itemsPerPage;
  const currentItems = filteredItems?.slice(itemOffset, endOffset);
  const pageCount = Math.ceil(filteredItems?.length / itemsPerPage);

  // Invoke when user click to request another page.
  const handlePageClick = (event) => {
    const newOffset = (event.selected * itemsPerPage) % filteredItems.length;
    console.log(
      `User requested page number ${event.selected}, which is offset ${newOffset}`
    );
    setItemOffset(newOffset);
  };

  return (
    <>
      <Items currentItems={currentItems} />
      <ReactPaginate
        breakLabel="..."
        nextLabel={<GrFormNext />}
        onPageChange={handlePageClick}
        pageRangeDisplayed={5}
        pageCount={pageCount}
        previousLabel={<GrFormPrevious />}
        renderOnZeroPageCount={null}
        className="pagination mt-3 fs-8"
      />
    </>
  );
}

export function Items({ currentItems }) {
  const navigate = useNavigate();

  const handleRedirect = (item) => {
    navigate(`/properties/${item?.id}`, { state: item?.id });
  };

  return (
    <div className="container p-0">
      <div className="row">
        {currentItems?.length > 0
          ? currentItems.map((item) => {
              return (
                <div className="col-lg-4 col-md-6 col-sm-12 d-flex justify-content-center">
                  <div
                    class="card property shadow border-0 rounded-0 mb-5 cursor-pointer"
                    onClick={() => handleRedirect(item)}
                  >
                    <img
                      src={
                        item?.imageLink?.match(/\.(jpeg|jpg|gif|png)$/) !== null
                          ? item?.imageLink
                          : noImg
                      }
                      class="propertyImage"
                      alt={item?.listingAddress}
                    />
                    <div
                      className="tags position-absolute end-0 pe-3"
                      style={{ bottom: "22%" }}
                    >
                      <span className="bg-primary-color rounded-pill p-1 px-3 fs-8">
                        {item.listingPropertyType}
                      </span>
                    </div>
                    <div class="card-body  ">
                      <p className="text-secondary-color fw-bold mb-1">
                        ${item?.listingRent}
                      </p>
                      <p className="mb-0 fs-8 text-secondary fw-bold">
                        {item?.listingAddress}
                      </p>
                    </div>
                    <div class="overlay">
                      <Button
                        className=" px-2 py-2 bg-primary-color border-0 rounded-0  ms-2 fs-9"
                        onClick={() => handleRedirect(item)}
                      >
                        Show More
                      </Button>
                    </div>
                  </div>
                </div>
              );
            })
          : ""
            // <div className="w-100 h-100 d-flex justify-content-center align-items-center">
            //   <Loading />
            // </div>
        }
      </div>
    </div>
  );
}
