import React from "react";
import { FaFileCircleCheck } from "react-icons/fa6";
import { Link } from "react-router-dom";

const Loading = ({ message }) => {
  return (
    <div className=" vw-80 vh-100 d-flex justify-content-center align-items-start mt-5 pt-5">
      <div className="d-flex flex-column justify-content-center align-items-center">
        <FaFileCircleCheck fontSize={100} color="#c1cd23" />

        <h3 className=" mt-3">{message}</h3>
        <p className="fs-9">
          It might take us a while to give you a prediction. Please check{" "}
          <Link to="/model/results">Prediction Result</Link> page to see if the
          result is out in a while.
        </p>
      </div>
    </div>
  );
};

export default Loading;
