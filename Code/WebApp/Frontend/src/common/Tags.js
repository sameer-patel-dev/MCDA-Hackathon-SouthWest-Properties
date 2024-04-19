import React from "react";

const Tags = ({ tags, setSelectedFilter, selectedFilter, label, show }) => {
  return (
    <div>
      {tags &&
        tags?.map((tag) => {
          return (
            <span
              class={`badge mx-2 my-1 px-3 py-2 rounded-pill ${
                selectedFilter[label]
                  ? selectedFilter[label] === tag
                    ? "bg-primary-color"
                    : "bg-light text-dark"
                  : "bg-light text-dark"
              }  cursor-pointer text-capitalize`}
              onClick={() =>
                setSelectedFilter((selectedFilter) => ({
                  ...selectedFilter,
                  [label]: tag,
                }))
              }
            >
              {tag === 4 || tag > 4 ? tag + "+ " + show : tag + " " + show}
              {/* {tag} {show} */}
            </span>
          );
        })}
    </div>
  );
};

export default Tags;
