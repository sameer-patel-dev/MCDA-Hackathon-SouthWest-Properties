import React from "react";

const LabelHeader = ({ title, icon }) => {
  return (
    <div className="d-flex align-items-center justify-content-start mb-2">
      {icon}
      <h6 className="text-capitalize mb-0 ms-2 fs-9 "> {title}</h6>
    </div>
  );
};

export default LabelHeader;
