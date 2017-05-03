 //<![cdata[
<!--

/*
 * File: sst.js
 * The JavaScript file used by SST JSP pages
 * Written by John Phan - NCC - Feb 2011
 */

var sstVariable;
var area;
var date;
var period;
var processing = false;
var compare = false;
var compareSize = 3;
var average = false;
var trend = false;
var dateInstances = new Array();
var runningInterval;
var runningAve = false;

function initialise() {
    setSstVariable();
    setArea();
    setPeriod();
    updatePage();
    setRunningInterval();
    toggleSlider();
}

function setSstVariable() {
    var object = document.getElementById('map');
    sstVariable = object.options[object.selectedIndex].value;
    decilesUpdate();
}

function decilesUpdate() {
    var perObj = document.getElementById('period');
    var areaObj = document.getElementById('area');
    var target = $('#datepicker');

    if (sstVariable == 'dec') {
        for (var index = 0; index < perObj.options.length; index++) {
            if(perObj.options[index].value == 'monthly') {
                perObj.options[index].disabled = false;
                perObj.options[index].selected = "selected";
            }
            else {
                perObj.options[index].disabled = "disabled";
            }
        }
//        for (var index = 0; index < areaObj.options.length; index++) {
//            if(areaObj.options[index].value == 'aus') {
//                areaObj.options[index].disabled = false;
//                areaObj.options[index].selected = "selected";
//            }
//            else if(areaObj.options[index].value == 'glob') {
//                areaObj.options[index].disabled = false;
//            }
//            else {
//                areaObj.options[index].disabled = "disabled";
//            }
//        }
    }
    else if (sstVariable == 'ice') {
        for (var index = 0; index < perObj.options.length; index++) {
            if(perObj.options[index].value == 'daily') {
                perObj.options[index].selected = "selected";
            }
            perObj.options[index].disabled = "";
        }
        for (var index = 0; index < areaObj.options.length; index++) {
            if ( areaObj.options[index].value == "glob") {
                areaObj.options[index].disabled = false;
            }
            else if(areaObj.options[index].value == 'sh') {
                areaObj.options[index].disabled = false;
                areaObj.options[index].selected = "selected";
            }
            else {
               areaObj.options[index].disabled = "disabled";
            }
        }
        target.datepick('enable');
    }
    else if (!average)  {
        for (var index = 0; index < perObj.options.length; index++) {
            if(perObj.options[index].value == 'daily') {
                perObj.options[index].selected = "selected";
            }
            perObj.options[index].disabled = "";
        }
        for (var index = 0; index < areaObj.options.length; index++) {
            if ( areaObj.options[index].value == "") {
                areaObj.options[index].disabled = "disabled";
            }
            else {
               areaObj.options[index].disabled = "";
            }
        }
        target.datepick('enable');
    }
    setArea();
    setPeriod();
}

function setArea() {
    var object = document.getElementById('area');
    area = object.options[object.selectedIndex].value; 
}

//function setDate(dateText, instance) {
//    date = dateText;
//}

function setDate(dateObj) {
    dateInstance = dateObj 
    if (average) {
        if (period == 'monthly'){
            date = $.datepick.formatDate('mm', dateInstance[0]);
        }
        else {
            date = $.datepick.formatDate('yyyy', dateInstance[0]);
        }
    }
    else {
        date = $.datepick.formatDate('yyyymmdd', dateInstance[0]);
    }
}

function setPeriod() {
    var object = document.getElementById('period');
    period = object.options[object.selectedIndex].value;
    target = $('#datepicker');
    inst = $('#datepicker').datepick('options');
//    $('#datepicker').datepick('setDate', null);
    if (period == 'weekly') {
       $('#datepicker').datepick('setDate', null);
    }
    if (average) {
//        $('#datepicker').datepick('setDate', null); 
        if (period == 'yearly') {
            $('#datepicker').datepick('disable');
        }
        else {
//            monthOnly()
            $('#datepicker').datepick('enable');
//            if (period == 'monthly') {
//                $('#datepicker').datepick('setDate', new Date(2010, 0, 1));
//                $('#datepicker').datepick('setDate', new Date(2010, 0, 1));
                
//            }
        } 
        if (period == 'monthly' && inst.dateFormat != 'MM') {
            target.datepick('option', {dateFormat: 'MM'});
            target.datepick('option', {maxDate: '+1y'});
        }
    }
    else {
        if (inst.dateFormat != 'dd M yyyy') {
            target.datepick('option', {dateFormat: 'dd M yyyy'});
            target.datepick('option', {maxDate: '-3D'});
        }
    }

}

function setCompare() {
    var object = document.getElementById('compare');
    compare = object.checked; 
}

function setTrend() {
    var object = document.getElementById('trend');
    trend = object.checked;
    if (runningAve && trend) {
        document.getElementById('runave').checked = false;
        runningAve = !trend;
    }
    toggleSlider();
}

function setRunningAve() {
    var object = document.getElementById('runave');
    runningAve = object.checked;
    if (runningAve && trend) {
        document.getElementById('trend').checked = false;
        trend = !runningAve;
    }
    toggleSlider()
}


function toggleSlider() {
    if (average && runningAve) {
        $( "#slide" ).slider( "option", "disabled", false );
    }
    else {
        $( "#slide" ).slider( "option", "disabled", true );
    }
}

function setAverage() {
    var object = document.getElementById('average');
    var trendCheck = document.getElementById('trend');
    var runningAveCheck = document.getElementById('runave');
    average = object.checked; 
    var object = document.getElementById('period');
    var mapObj = document.getElementById('map');
    var target = $('#datepicker');
//    setSstVariable()
    if (average) {
        trendCheck.disabled = false;
        runningAveCheck.disabled = false;
        for (var index = 0; index < object.options.length; index++) {
            if(object.options[index].value == 'monthly') {
                object.options[index].disabled = false;
                object.options[index].selected = "selected";
            }
            else if(object.options[index].value == 'yearly') {
                object.options[index].disabled = false;
            }   
            else {
                object.options[index].disabled = "disabled";
            } 
        }
        for (var index = 0; index < mapObj.options.length; index++) {
            if(mapObj.options[index].value == 'anom') {
                mapObj.options[index].disabled = false;
                mapObj.options[index].selected = "selected";
            }
            else {
                mapObj.options[index].disabled = "disabled";
            } 
        }
    }
    else {
        trendCheck.disabled = "disabled";
        runningAveCheck.disabled = "disabled";
        for (var index = 0; index < object.options.length; index++) {
            if(object.options[index].value == 'daily') {
                object.options[index].selected = "selected";
            }
            object.options[index].disabled = "";
        }
        for (var index = 0; index < mapObj.options.length; index++) {
            if(mapObj.options[index].value == 'mean') {
                mapObj.options[index].selected = "selected";
            }
            mapObj.options[index].disabled = "";
        }
        target.datepick('enable'); 
    }
    setSstVariable();
    setPeriod()
    setDate(dateInstance)
    toggleSlider();
//    target.datepick('setDate', null); 
//    target.datepick('setDate', new Date(2010, 0, 1)); 
}

function setRunningInterval(){
    runningInterval = $( "#slide" ).slider( "value" )
    document.getElementById('slideval').innerHTML = runningInterval;
}

function setRunningMeanInterval(event, ui) {
    runningInterval = ui.value;
    document.getElementById('slideval').innerHTML = runningInterval;
}

function monthOnly(picker, inst){
    var target = $('#datepicker');
    if(!average) {
        var selectMonth = $('<div style="text-align: center;"><button type="button">Select</button></div>').
            insertAfter(picker.find('.datepick-month-row:last,.ui-datepicker-row-break:last')).
            children().click(function() {
                var monthYear = picker.find('.datepick-month-year:first').val().split('/');
                target.datepick('setDate', $.datepick.newDate(
                    parseInt(monthYear[1], 10), parseInt(monthYear[0], 10), 1)).
                    datepick('hide');
            });
    }
    picker.find('.datepick-month-row table,.ui-datepicker-row-break table').remove();
    if(average) {
        picker.find('.datepick-month-year')[1].disabled = true;
//        if(target.datepick("getDate").length == 0
//            || target.datepick("getDate")[0].getFullYear() != 2010) {
//            target.datepick('setDate', new Date(2010, 1, 1));
//        }
//        picker.find('.datepick-month-year')[1].selectedIndex = 0;
    }
}

function yearOnly(picker, inst){
    var target = $('#datepicker');
//    var selectMonth = $('<div style="text-align: center;"><button type="button">Select</button></div>').
//        insertAfter(picker.find('.datepick-month-row:last,.ui-datepicker-row-break:last')).
//        children().click(function() {
//            var monthYear = picker.find('.datepick-month-year:first').val().split('/');
//            target.datepick('setDate', $.datepick.newDate(
//                parseInt(monthYear[1], 10), parseInt(monthYear[0], 10), 1)).
//                datepick('hide');
//        });
    picker.find('.datepick-month-row table,.ui-datepicker-row-break table').remove();
    picker.find('.datepick-month-year')[0].disabled = true;
    picker.find('.datepick-month-year')[0].selectedIndex = 0;
}

function weekOnly(picker, inst){
    var target = $('#datepicker');
//    var target = $(this);
    picker.find('td.datepick-week span,td.ui-state-hover span').each(function() {
        $('<a href="javascript:void(0)" class="' +
            this.className + '" title="Select the entire week">' +
            $(this).text() + '</a>').
                click(function() {
                    var date = target.datepick('retrieveDate', this);
                    var dates = [date];
                    for (var i = 1; i < 7; i++) {
                        dates.push(date = $.datepick.add($.datepick.newDate(date), 1, 'd'));
                    }
                    if (inst.get('rangeSelect')) {
                        dates.splice(1, dates.length - 2);
                    }
                        target.datepick('setDate', dates).datepick('hide');
                    }).
                replaceAll(this);
            });
}

function checkPeriod() {
    if (period == 'weekly') {
        return {selectable: false};
    }
    else {
        return {selectable: true};
    }
}

function closed(dates) {
//    alert('Closed with date(s): ' + dates);
//    alert($("*:focus"))
//    $("#datepicker").datepick('hide');
}


function monthOrYearChanged(year, month) {
    if(average || period == 'yearly') {
        var target = $('#datepicker');
        if(period == 'yearly') {
            target.datepick('setDate', $.datepick.newDate(
                parseInt(year, 10), 1, 1)).
                datepick('hide');   
        }
        else {
            target.datepick('setDate', $.datepick.newDate(
                parseInt(year, 10), parseInt(month, 10), 1)).
                datepick('hide');   
        }
    } 
}


function beforeShow(picker, inst) {
//    alert( $('#datepicker').datepick('getDate'))
    if (period == 'monthly' || period == '3monthly' || period == '6monthly') {
        monthOnly(picker, inst);
    }
    else if (period == 'yearly') {
        yearOnly(picker, inst);
    }
    else if (period == 'weekly'){
        weekOnly(picker, inst);
    }
}

function updatePage() {
    if (!date) {
        if (average && period == 'yearly') {
            date = '9999';
        }
        else {
            date = document.getElementById('datepicker').value;
        }
    }
    if (!date) {
        alert('Please specify a date first.');
    }
    else if (processing) {
    }
    else {
        processing = true;
        request = new ajaxRequest();
        url =  "http://tuscany.bom.gov.au/cgi-bin/reynoldsSst.py?map=" + sstVariable 
                 + "&date=" + date 
                 + "&area=" + area
                 + "&period=" + period
                 + "&average=" + average
                 + "&trend=" + trend
                 + "&runningAve=" + runningAve
                 + "&runningInterval=" + runningInterval
                 + "&timestamp=" + new Date()
        request.open("GET", url, true)
        request.withCredentials = "true"
        request.onreadystatechange = function() {
            if (this.readyState == 4) {
               processing = false
               if (this.status == 200) {
                   if (this.responseText != null) {
                       var son = eval('(' + this.responseText + ')');
                       if (compare){
                           var imgDiv = document.getElementById('mainImg');
                           var imgList = imgDiv.childNodes;
                           //This is to remove the loading flower image.
                           imgDiv.removeChild(imgDiv.firstChild);
                           if (imgList.length >= compareSize) {
                               imgDiv.removeChild(imgDiv.lastChild);
                           }
                           var img = document.createElement("IMG");
                           if(average) {
                               img.src = son.aveImg;
                               img.width = "680";
                               document.getElementById('aveArea').innerHTML = '<div style="display:inline-block; width:341px; text-align:left">Download data from <a href="' + son.aveData + '" target="_blank">here</a></div>' 
                                                                            + '<div style="display:inline-block; width:341px; text-align:right"><b>Average(1981-2010)</b> ' + Math.round(son.mean*100)/100 + '\u00B0C</div>'
                           }
                           else if (son.img != null) {
                               img.src = son.img;
                               img.width = "680";
                               document.getElementById('aveArea').innerHTML = ''
                           }
                           else {
                               img.src = "images/notavail.png";
                               document.getElementById('aveArea').innerHTML = ''
                           }
                           imgDiv.insertBefore(img, imgDiv.firstChild);
                               
                       }
                       else {
                           if (average) {
                               document.getElementById('mainImg').innerHTML = '<img src="' + son.aveImg + '" width="680"/>'
                               document.getElementById('aveArea').innerHTML = '<div style="display:inline-block; width:341px; text-align:left">Download data from <a href="' + son.aveData + '" target="_blank">here</a></div>' 
                                                                            + '<div style="display:inline-block; width:341px; text-align:right"><b>Average(1981-2010)</b> ' + Math.round(son.mean*100)/100 + '\u00B0C</div>'
                           }
                           else if (son.img != null) {
                               document.getElementById('mainImg').innerHTML = '<img src="' + son.img + '" width="680"/>'
                               document.getElementById('aveArea').innerHTML = ''
                           }
                           else if (son.error != null) {
//                               document.getElementById('mainImg').innerHTML = '<p>' + son.error + '</p>';
                               document.getElementById('mainImg').innerHTML = '<img src="images/notavail.png" />';
                               document.getElementById('aveArea').innerHTML = ''
                           }
                       }
                   }
                   else
                       alert("Ajax error: " + this.statusText)
               }
               else 
                   alert("Ajax error: " + this.statusText)
            }
        }
//        document.getElementById('mainImg').innerHTML = '<div style="width:683px; height:300px; text-align: center; vertical-align: middle; display:table-cell;"> <img src="images/loading.gif" /> </div>';
        document.getElementById('mainImg').innerHTML = '<img src="images/loading.gif" />' + document.getElementById('mainImg').innerHTML; 
        request.send(null)
    }
}

function ajaxRequest() {
    try {
        var request = new XMLHttpRequest()
    }
    catch(e1) {
        try {
            request = new ActiveXObject("Msxml2.XMLHTTP")
        }
        catch(e2) {
            try {
                request = new ActiveXObject("Microsoft.XMLHTTP")
            }
            catch(e3) {
                request = false
            }
        }
    }
    return request
}

//-->
//]]>

