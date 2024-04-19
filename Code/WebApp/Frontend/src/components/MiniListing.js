import React, { useState } from "react";
import ReactPaginate from "react-paginate";
import { GrFormPrevious, GrFormNext } from "react-icons/gr";
import { useNavigate } from "react-router-dom";
import noImg from "../assets/img/no-img.jpg";

const MiniListing = ({ filteredItems, handleMouseEvent }) => {
  return (
    <div className="miniSidebar bg-white">
      <PaginatedItems
        // filter={filter}
        filteredItems={filteredItems}
        itemsPerPage={8}
        handleMouseEvent={handleMouseEvent}
      />
    </div>
  );
};

export default MiniListing;

export function PaginatedItems({
  itemsPerPage,
  filteredItems,
  handleMouseEvent,
}) {
  // Here we use item offsets; we could also use page offsets
  // following the API or data you're working with.
  const [itemOffset, setItemOffset] = useState(0);

  // Simulate fetching items from another resources.
  // (This could be items from props; or items loaded in a local state
  // from an API endpoint with useEffect and useState)

  const endOffset = itemOffset + itemsPerPage;
  const currentItems = filteredItems?.slice(itemOffset, endOffset);
  const pageCount = Math.ceil(filteredItems.length / itemsPerPage);

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
      <MiniItems
        currentItems={currentItems}
        handleMouseEvent={handleMouseEvent}
      />
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

export const MiniItems = ({ currentItems, handleMouseEvent }) => {
  const navigate = useNavigate();

  const handleRedirect = (item) => {
    navigate(`/properties/${item?.id}`, { state: item?.id });
  };
  return (
    <>
      <div className="">
        {currentItems?.map((item, idx) => {
          return (
            <div
              className="d-flex shadow m-2 mb-4 cursor-pointer"
              onClick={() => handleRedirect(item)}
              onMouseOver={() => handleMouseEvent(item)}
              onMouseOut={() => handleMouseEvent({})}
            >
              <img
                src={
                  item?.imageLink?.match(/\.(jpeg|jpg|gif|png)$/) !== null
                    ? item?.imageLink
                    : noImg
                }
                class=" me-3 border-0 "
                alt={item?.listingAddress}
              />
              <div className="pt-3 pe-2">
                <h4 class="card-text fs-9">{item?.listingAddress}</h4>
                <p className="text-secondary-color fw-bold mb-1">
                  ${item?.listingRent}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
};
