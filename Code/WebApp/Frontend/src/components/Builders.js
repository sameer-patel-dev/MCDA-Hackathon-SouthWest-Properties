import React, { useEffect, useState } from "react";
import Loading from "../components/Loading";
import { FaLocationDot, FaRegBuilding } from "react-icons/fa6";

import { instance } from "../config/config";
const Builders = () => {
  const [data, setData] = useState();

  useEffect(() => {
    instance
      .get("/api/builders")
      .then((res) => {
        // Assuming the response data is the array you want to display
        setData(res.data); // Update the state with the fetched data
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <>
      <div className="container pt-5">
        <h5>Upcoming Projects</h5>
        <div className="row">
          {data?.length > 0 ? (
            data?.map((build, idx) => {
              return (
                <div className="col-lg-4 col-md-4 col-sm-12 my-3" key={idx}>
                  <div className="builder-card border-0 p-2">
                    <div className="d-flex justify-content-between align-items-center">
                      <h6 className="fw-bold">{build?.projectName}</h6>
                      <span
                        class={`badge rounded-pill bg-success mx-2 my-1 px-3 py-2 `}
                      >
                        {build?.projectStatus}
                      </span>
                    </div>
                    <p className="mb-1 text-primary-color fs-9">
                      <FaLocationDot />
                      {build?.projectLocation}
                    </p>
                    <p className="mb-1 fs-9">
                      <FaRegBuilding />
                      {build?.projectBuilder}
                    </p>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="w-100 d-flex justify-content-center align-items-center">
              <Loading />
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Builders;
