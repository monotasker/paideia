import { useLocation } from "react-router-dom";

// load scripts dynamically as needed by a component
const loadScriptByURL = (id, url, callback) => {
    const isScriptExist = document.getElementById(id);

    if (!isScriptExist) {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = url;
    script.id = id;
    script.onload = function () {
        if (callback) callback();
    };
    document.body.appendChild(script);
    }

    if (isScriptExist && callback) callback();
}

const useQuery = () => {
  return new URLSearchParams(useLocation().search);
}

export {
    loadScriptByURL,
    useQuery
}