// Usar este arquivo para testar js que está no HTML

async function callback() {
   let municipio = document.getElementById("municipio").value;
   let fito = document.getElementById("fito_ecologica").value;
   let latlong = document.getElementById("lat_long").value;
   let CAR = document.getElementById("CAR").value;
   if (latlong.startsWith("(")) latlong = "";
   if (CAR.startsWith("(")) CAR = "";
   try {
     document.body.style.cursor = 'progress';
     let response = await fetch(`/callback/getMunicipioFito?&idMunicipio=${municipio}&idFito=${fito}&latlong=${latlong}&CAR=${CAR}`);
     if (!response.ok) {
       alert(`HTTP-Error: ${response.status} on callback().`);
     } else {
       let jsoData = await response.json();
       if (!response.ok) {
         alert(`HTTP-Error: ${response.status} on json response.`);
       } else {
         const jsFitoMun = JSON.parse(jsoData["FitoMunicipio"]);
         let newHTML = "";
         for (const [key, value] of Object.entries(jsFitoMun)) {
           newHTML = newHTML + `<option value='${key}'>${value}</option>`;
         }
         document.getElementById("fito_ecologica").setHTML(newHTML);
         Plotly.react("map", JSON.parse(jsoData["Map"]), {});
         document.getElementById("area").value = jsoData["Area"];
       }
     }
   } finally {
     document.body.style.cursor = 'default';
   }
 }
