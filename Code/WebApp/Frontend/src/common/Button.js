import React from "react";

const Button = ({ children, className, onClick, disabled }) => {
  // console.log(disabled);
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      className={`border-0 ${className} ${
        disabled ? "bg-secondary" : "bg-primary-color"
      }  p-1 px-4  rounded-pill text-center`}
    >
      {children}
    </button>
  );
};

export default Button;
