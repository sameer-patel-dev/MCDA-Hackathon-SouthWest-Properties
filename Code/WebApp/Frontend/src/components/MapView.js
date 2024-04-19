import React, { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const MapView = ({ filteredItems, itemToshow }) => {
  const mapRef = useRef();

  const [markers, setMarkers] = useState([]);

  const icon = L.icon({
    iconSize: [25, 41],
    iconAnchor: [10, 41],
    popupAnchor: [2, -40],
    iconUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-shadow.png",
  });

  const getAllMarkers = () => {
    // console.log("@filteredItems", filteredItems);
    const uniqueMarkerPositions = new Set();

    // Filter out duplicate markers and update markers state
    setMarkers(
      filteredItems
        ?.filter(
          (item) =>
            item?.listingLatitude !== null && item?.listingLongitude !== null
        )
        ?.flatMap((item) => {
          const position = `${item?.listingAddress}`;
          // Check if the position is already in the Set
          if (!uniqueMarkerPositions.has(position)) {
            // If not, add it to the Set and return the marker object
            uniqueMarkerPositions.add(position);
            return [
              {
                position: [item?.listingLatitude, item?.listingLongitude],
                name: item?.listingAddress,
                description: item?.listingMajorRegion,
                property_type: item?.listingPropertyType,
                rent_range: item?.listingRent,
              },
            ];
          }
          return []; // Return an empty array for duplicate markers
        })
    );
  };

  useEffect(() => {
    if (
      itemToshow &&
      Object?.keys(itemToshow)?.length !== 0 &&
      itemToshow?.listingLatitude !== null &&
      itemToshow?.listingLongitude !== null
    ) {
      setMarkers([
        {
          position: [itemToshow?.listingLatitude, itemToshow?.listingLongitude],
          name: itemToshow?.listingAddress,
          description: itemToshow?.listingMajorRegion,
          property_type: itemToshow?.listingPropertyType,
          rent_range: itemToshow?.listingRent,
        },
      ]);
      mapRef?.current?.openPopup();
    } else {
      mapRef?.current?.closePopup();
    }
  }, [itemToshow]);

  useEffect(() => {
    getAllMarkers();
  }, [filteredItems]);

  return (
    <>
      <MapContainer
        center={[44.6514672, -63.6537874]}
        zoom={13}
        ref={mapRef}
        style={{ height: "50vh", width: "52vw", left: "15%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers?.map((marker, index) => (
          <Marker
            ref={mapRef}
            key={index}
            position={marker?.position}
            icon={icon}
            eventHandlers={{
              mouseover: (e) => {
                e.target.openPopup();
              },
              mouseout: (e) => {
                e.target.closePopup();
              },
              click: (e) => {
                console.log("clicked");
                console.log(e);
              },
            }}
          >
            <Popup>
              <div>
                <h6 className="">{marker?.name}</h6>
                <p className="my-3 fs-9">
                  <span className="px-2 py-1 rounded-pill bg-primary-color text-capitalize">
                    {marker?.property_type}{" "}
                  </span>

                  <span className="px-2 py-1 mx-2 rounded-pill bg-primary-color text-capitalize">
                    ${marker?.rent_range}
                  </span>
                </p>
                <p className="fs-9 mt-0">{marker?.description}</p>
              </div>
            </Popup>
          </Marker>
        ))}
        {/* Additional map layers or components can be added here */}
      </MapContainer>
    </>
  );
};

export default MapView;
