async function getDistribution() {
  const response = await fetch('/callback/getDistribution')
  if (!response.ok) {
    setFitoMsg(sFitoErr);
    alert(`HTTP-Error: ${response.status} on callback().`);
  } else {
    const jsoRsp = await response.json();
    const jsData = jsoRsp.data;// já é jso  JSON.parse(jsoData["data"]);

    imgData = [];
    for (let i = 0; i < jsData.length; i += 2) {
      imgData.push({ caption: jsData[i].descModelo, file: jsData[i + 1].ArquivoDesenho });
    }

    const iColCount = 2;
    let i = 0;
    let sHtml = ''
    imgData.forEach(itm => {
      if (i == 0) { sHtml += ((sHtml == '') ? '' : '</div>') + '<div class="row">'; }
      sHtml += '<div class="col">' +
        `<img src="../../assets/img/modelo_plantio/${itm.file}" alt="${itm.file}">` +
        '<br>' +
        `<button type="button" class="btn btn-info" onclick="">${itm.caption}</button>` +
        '</div>';
      i = (i >= iColCount) ? 0 : i + 1;
    });
  }
}
