/*自动加载省份列表*/
function showProv(province) {
    prov = province;
    var len = provice.length;
    for (var i = 0; i < len; i++) {
        var provOpt = document.createElement('option');
        provOpt.innerText = provice[i]['name'];
        provOpt.value = i;
        prov.append(provOpt);
    }
}
function showCmbProv(prov) {
    var len = provice.length;
    for (var i = 0; i < len; i++){
        var cmbProvOpt = document.createElement('option');
        cmbProvOpt.innerText = provice[i]['name'];
        cmbProvOpt.value = i;
        prov.append(cmbProvOpt);
    }
}

/*根据所选的省份来显示城市列表*/
function showCity(province, city, area, format_school) {
    var province_id = province.val();
    city.empty();
    city.append("<option>=请选择城市=</option>");
    area.empty();
    area.append("<option>=请选择县区=</option>");
    format_school.empty();
    format_school.append("<option value='0'>=请选择学校=</option>");
    if (province_id != "=请选择省份=") {
        var cityLen = provice[province_id]["city"].length;
        for (var j = 0; j < cityLen; j++) {
            var cityOpt = document.createElement('option');
            cityOpt.innerText = provice[province_id]["city"][j].name;
            cityOpt.value = j;
            city.append(cityOpt);
        }
    }
}
function showCmbCity(cmbProvince, cmbCity, cmbArea) {
    var province_id = cmbProvince.val();
    cmbCity.empty();
    cmbCity.append("<option>=请选择城市=</option>");
    cmbArea.empty();
    cmbArea.append("<option>=请选择县区=</option>");
    if (province_id != "=请选择省份=") {
        var cmbCityLen = provice[province_id]["city"].length;
        for (var j = 0; j < cmbCityLen; j++) {
            var cmbCityOpt = document.createElement('option');
            cmbCityOpt.innerText = provice[province_id]["city"][j].name;
            cmbCityOpt.value = j;
            cmbCity.append(cmbCityOpt);
        }
    }
}

/*根据所选的城市来显示县区列表*/
function showCountry(province, city, area, format_school) {
    var province_id = province.val();
    var city_id = city.val();
    area.empty();
    area.append("<option>=请选择县区=</option>");//清空之前的内容只留第一个默认选项
    format_school.empty();
    format_school.append("<option value='0'>=请选择学校=</option>");
    if (city_id != "=请选择城市=") {
        var countryLen = provice[province_id]["city"][city_id].districtAndCounty.length;
        if(countryLen == 0){
            return;
        }
        for (var n = 0; n < countryLen; n++) {
            var countryOpt = document.createElement('option');
            countryOpt.innerText = provice[province_id]["city"][city_id].districtAndCounty[n];
            countryOpt.value = n;
            area.append(countryOpt);
        }
    }
}
function showCmbCountry(cmbProvince, cmbCity, cmbArea) {
    var province_id = cmbProvince.val();
    var city_id = cmbCity.val();
    cmbArea.empty();
    cmbArea.append("<option>=请选择县区=</option>");//清空之前的内容只留第一个默认选项
    if (city_id != "=请选择城市=") {
        var cmbCountryLen = provice[province_id]["city"][city_id].districtAndCounty.length;
        if(cmbCountryLen == 0){
            return;
        }
        for (var n = 0; n < cmbCountryLen; n++) {
            var cmbCountryOpt = document.createElement('option');
            cmbCountryOpt.innerText = provice[province_id]["city"][city_id].districtAndCounty[n];
            cmbCountryOpt.value = n;
            cmbArea.append(cmbCountryOpt);
        }
    }
}

/*选择县区之后的处理函数*/
function selecCountry(province, city, area, format_school) {
    var city_id = city.val();
    var area_id = area.val();

    format_school.empty();
    format_school.append("<option value='0'>=请选择学校=</option>");
    if ((city_id != "=请选择城市=") && (area_id != "=请选择县区=")) {
        getFormatSchool(province.find("option:selected").text(), city.find("option:selected").text(), area.find("option:selected").text(), format_school);
    }
}
function selecCmbCountry(cmbProvince, cmbCity, cmbArea) {
    // cmbCurrent.cmbArea = obj.options[obj.selectedIndex].value;
    // if ((cmbCurrent.cmbCity != null) && (cmbCurrent.cmbArea != null)) {
    //     // btn.disabled = false;
    // }
}