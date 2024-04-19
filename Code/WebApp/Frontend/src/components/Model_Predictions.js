import React, { useEffect, useState } from "react";
import { instance } from "../config/config";
import Loading from "./Loading";

const Model_Predictions = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    setLoading(true);
    instance
      .get("/api/forecast/results")
      .then((res) => {
        if (res?.data && res?.data?.files?.length > 0) {
          const cleanedFiles = res?.data?.files
            ?.filter((file) => file?.endsWith(".csv")) // Filter only CSV files
            ?.map((file) => file?.replace("Model/Output/", ""));
          setFiles(cleanedFiles);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  }, []);

  const getDate = (filename) => {
    const parts = filename.split("/");

    const date_with_extension = parts[1];

    const date_part = date_with_extension.split(".")[0];

    return date_part;
  };

  const downloadFile = (file) => {
    setLoading(true);

    instance
      .get(`/api/download_file?file_name=${file}`)
      .then((res) => {
        if (res?.data) {
          try {
            setLoading(false);
            const link = document.createElement("a");
            link.href = res?.data?.url;
            link.setAttribute("download", file);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          } catch (error) {
            console.error("Error downloading file:", error);
          }
        }
      })
      .catch((err) => {
        setLoading(false);

        console.log(err);
      });
  };
  return (
    <>
      <div className="container mt-3 prediction">
        <h6 className="my-4 fw-bold">
          Results of all the files you've uploaded. You can download the result
          by clicking on the filename
        </h6>
        <div className="table-responsive">
          <table class="table table-bordered fs-9">
            <thead>
              <tr>
                <th scope="col">S.N</th>
                <th scope="col">Date</th>
                <th scope="col">Result</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <div className="d-flex justify-content-center align-items-center my-2 w-100">
                  <Loading />
                </div>
              ) : files?.length > 0 ? (
                files?.map((file, idx) => {
                  return (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>{getDate(file)}</td>
                      <td
                        className="cursor-pointer text-decoration-underline fileName"
                        onClick={() => downloadFile(file)}
                      >
                        {file}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td className="fs-9">
                    No result yet! Please wait for a while
                  </td>
                </tr>
              )}
              <tr></tr>
            </tbody>
          </table>
        </div>
        <p>{loading}</p>
      </div>
    </>
  );
};

export default Model_Predictions;
