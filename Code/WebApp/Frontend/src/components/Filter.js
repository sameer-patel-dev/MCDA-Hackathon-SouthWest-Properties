import React, { useEffect, useState } from "react";
import { BsBuildingsFill } from "react-icons/bs";
import { RiMoneyDollarCircleFill } from "react-icons/ri";
import { FaBed } from "react-icons/fa";
import { GiBathtub } from "react-icons/gi";
import {
  MdOutlinePets,
  MdOutlineKeyboardDoubleArrowLeft,
} from "react-icons/md";
import LabelHeader from "../common/LabelHeader";
import Dropdown from "../common/Dropdown";
import Tags from "../common/Tags";
import Button from "../common/Button";

const Filter = ({ handleFilter, clearAll, className, allData }) => {
  const [data, setData] = useState({
    listingPropertyType: [],
    bedroomCount: [1, 2, 3, 4],
    bathroomCount: [1, 2, 3, 4],
    listingRent: "",
  });
  const [selectedFilter, setSelectedFilter] = useState({});

  useEffect(() => {
    // Function to extract unique values for each key
    const extractUniqueValues = () => {
      const propertyTypes = [
        ...new Set(allData?.map((item) => item["listingPropertyType"])),
      ];

      setData((data) => ({
        ...data,
        listingPropertyType: propertyTypes,
      }));
    };

    // Call the function to extract unique values when component mounts
    extractUniqueValues();
  }, [allData]);

  const onPropertyChange = (e) => {
    setSelectedFilter((selectedFilter) => ({
      ...selectedFilter,
      listingPropertyType: e?.target?.value,
    }));
  };

  const onPriceChange = (e) => {
    e?.preventDefault();
    const { name, value } = e?.target;

    // Parse the input value to a float
    const parsedValue = parseFloat(value);
    setSelectedFilter((selectedFilter) => ({
      ...selectedFilter,
      listingRent: {
        // Spread the existing listingRent object
        ...selectedFilter.listingRent,
        // Update minVal or maxVal based on the input name
        [name]: parsedValue,
      },
    }));
  };

  const clearFilter = (e) => {
    e?.preventDefault();
    setSelectedFilter({});
    clearAll();
  };

  // console.log(selectedFilter);
  return (
    <div>
      <div className={`${className}   px-3`}>
        <div className="py-3 custom-bottom">
          <LabelHeader title="Property Type" icon={<BsBuildingsFill />} />
          <Dropdown
            options={data?.listingPropertyType}
            title="Property Type"
            name="listingPropertyType"
            value={selectedFilter?.listingPropertyType || ""}
            onChange={onPropertyChange}
          />
        </div>
        <div className="py-3 custom-bottom">
          <LabelHeader title="Price" icon={<RiMoneyDollarCircleFill />} />
          <div className="d-flex">
            <form class=" price d-flex justify-content-between">
              <div>
                <input
                  type="number"
                  class="form-control"
                  name="minVal"
                  id="minVal"
                  placeholder="0"
                  onChange={onPriceChange}
                  value={selectedFilter?.listingRent?.minVal || ""}
                />
                <label for="minVal" className="fs-8 text-primary-color">
                  Min
                </label>
              </div>
              <div className="ms-2">
                <input
                  type="number"
                  class="form-control "
                  id="maxVal"
                  name="maxVal"
                  placeholder="3000"
                  onChange={onPriceChange}
                  value={selectedFilter?.listingRent?.maxVal || ""}
                />
                <label for="maxVal" className="fs-8 text-primary-color">
                  Max
                </label>
              </div>
            </form>
          </div>
        </div>

        <div className="py-3 custom-bottom">
          <LabelHeader title="Bedroom" icon={<FaBed />} />
          <Tags
            show="bed"
            label="bedroomCount"
            tags={data?.bedroomCount}
            setSelectedFilter={setSelectedFilter}
            selectedFilter={selectedFilter}
          />
        </div>

        <div className="py-3 custom-bottom">
          <LabelHeader title="Bath" icon={<GiBathtub />} />
          <Tags
            show="bath"
            label="bathroomCount"
            tags={data?.bathroomCount}
            setSelectedFilter={setSelectedFilter}
            selectedFilter={selectedFilter}
          />
        </div>

        <div className=" d-flex justify-content-center align-items-center mt-3">
          <Button onClick={() => handleFilter(selectedFilter)}>Filter</Button>
          <Button className={"bg-black mx-3"} onClick={clearFilter}>
            Clear All
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Filter;
