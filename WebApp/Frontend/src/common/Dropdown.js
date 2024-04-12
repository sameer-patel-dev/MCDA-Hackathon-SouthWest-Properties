import React from "react";

const Dropdown = ({ options, className, title, onChange, name, value }) => {
  return (
    <>
      <select
        class={`form-select ${className}`}
        aria-label="Default select example"
        onChange={onChange}
        name={name}
        value={value}
      >
        <option selected>Select {title}</option>
        {options &&
          options?.map((option, key) => {
            return (
              <>
                <option value={option} className="text-capitalize">
                  {option}
                </option>
              </>
            );
          })}
      </select>
    </>
  );
};

export default Dropdown;
