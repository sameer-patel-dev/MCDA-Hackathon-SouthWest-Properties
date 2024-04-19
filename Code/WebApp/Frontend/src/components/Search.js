import React from "react";

const Search = ({ searchTerm, handleSearch }) => {
  return (
    <>
      {" "}
      <div class="input-group w-50">
        <input
          type="text"
          class="form-control border-0 border-bottom rounded-0 fs-9 py-1 px-0 w-100"
          placeholder="Search by property name ..."
          aria-label="name"
          aria-describedby="basic-addon1"
          value={searchTerm}
          onChange={handleSearch}
        />
      </div>
    </>
  );
};

export default Search;
