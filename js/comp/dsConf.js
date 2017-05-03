/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

/* Dataset specific overrides */

var ocean = ocean || {};

ocean.sliderdownloadlink = '';

var location_missing_msg = "Please click on the map to select a location.";

function override(paramsfunc) {
    return function () {
        /* default parameters */
        out = {
            dataset: getBackendId(ocean.datasetid),
            variable: getBackendId(ocean.datasetid, ocean.variable),
            plot: ocean.plottype,
            date: $.datepick.formatDate('yyyymmdd', ocean.date),
            period: ocean.period,
            area: ocean.area,
            timestamp: $.now()
        };

        if (paramsfunc) {
            $.extend(out, paramsfunc(ocean.dataset));
        }

        return out;
    };
}

ocean.dsConf = {
    reynolds: {
        params: override(function (dataset) { return {
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        beforeSend: function() {
            valid = true;
            if (!ocean.date) {
                valid = false;
            }
            return valid; 
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            if (ocean.variable == 'sstanom' &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data);
            }
            else if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                //updateMapTiles('reynolds', data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            if (ocean.variable == 'sstdec') {
                disablePointClick();
            }
            else {
                enablePointClick();
            }
           // enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
            if (ocean.variable == 'sstdec') {
                disablePointClick();
            }
            else {
                enablePointClick();
            }
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    ersst: {
        params: override(function (dataset) { return {
            baseYear: 1950,
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            prependOutputSet();

            if (ocean.variable == 'sstanom' &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data
                             );

            }
            else if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            if (ocean.variable == 'sstdec') {
                disablePointClick();
            }
            else {
                enablePointClick();
            }
           // enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
            if (ocean.variable == 'sstdec') {
                disablePointClick();
            }
            else {
                enablePointClick();
            }
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(2);
        }


    },
    bran: {
        params: override(function (dataset) {
            switch (ocean.plottype) {
              case 'xsections':
                  return { lat: $('#latitude').val(),
                           lon: $('#longitude').val() };
                  break;

              default:
                  return {};
            }

            return params;
        }),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            var plottype = ocean.plottype;
            if ((["salt", "temp"].indexOf(variable) != -1) && (["xsections"].indexOf(plottype) != -1)){
                valid = isLocationPointValid();
                if (!valid){
                    text = location_missing_msg;
                }
            }

            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid;
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    ww3: {
        params: override(function (dataset) { return {
            lllat: $('#latitude').val(),
            lllon: $('#longitude').val(),
            urlat: $('#latitude').val(),
            urlon: $('#longitude').val(),
            step: $('#hour').val()
        };}),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            if (["atlas"].indexOf(variable) == -1 && ocean.dataset.params().plot != 'map') { //All variables under ww3 except wave atlas
                valid = isLocationPointValid();
                if (!valid){
                    text = location_missing_msg;
                }
            }

            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid;
        },
        callback: function(data) {
            prependOutputSet();
            periodStr = ocean.dataset.params()["period"];

            if (periodStr == "monthly"){
                if(data.ext != null) {
                    appendOutput(data.img, data.ext);
                }
            } else if  (periodStr == "hourly"){
              if (data.img != null && data.scale != null){
                    prependOutputSet();
                    appendOutput(data.img, null, null, null, data);
                   // updateMap(data.mapimg);

                    var overlayimg;
                    if(data.arrow) {
                        overlayimg = data.arrow;
                    }
                    updateMapTiles(data.map, data.mapimg, overlayimg);
                    setLegend(data.scale);
                }
            }
        },
        onSelect: function(){
            $('#plottype').change();
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function(){
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            if (ocean.variable == 'Tm') {
                return value.toFixed(0);
            }
            else if (ocean.variable == 'Hs') {
                return value.toFixed(1);
            }
        }

    },
    ww3forecast: {
        params: override(function (dataset) { return {
                'step' : slider.getStep()[0] - 1
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime + 'UTC');
                    //display local time
                    var dt = forecast[this.getStep()[0] - 1].datetime
                    var local = getLocalTime(dt);
                    $('.slider-hint').text(local.toString());
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        //updateMap(data.mapimg);
                        var overlayimg;
                        if(data.label) {
                            overlayimg = data.label;
                        }
                        if(data.arrow) {
                            overlayimg = data.arrow;
                        }
                        if (overlayimg) {
                            overlayimg = overlayimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        }
                        overlayimg = overlayimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        //updateMapTiles(data.map, data.mapimg, overlayimg);
                        if (!hasResultOverlay()){
                            updateMapTiles(data.map, data.mapimg, overlayimg);
                        }

                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        //updateMap(data.mapimg);
                        var overlayimg;
                        if(data.label) {
                            overlayimg = data.label;
                        }
                        if(data.arrow) {
                            overlayimg = data.arrow;
                        }
                        if (overlayimg) {
                            overlayimg = overlayimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        }
                        updateMapTiles(data.map, data.mapimg, overlayimg);
                        doPointClick();
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function() {
            updatePage();
            resetPointClick();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:'',
        formatValue: function(value) {
            return value.toFixed(1);
        }
    },
    waveatlas: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
        },
        onSelect: function(){
            if (ocean.variable == 'atlas'){
                ocean.dsConf.ww3.overlay = new L.FeatureGroup();

                //Read file
                $.getScript( "js/comp/data_points_to_load.js")

                  .done(function( script, textStatus ) {
                    //Load the markers
                    for (var i = 0; i < points.length; i++) {
                        var marker = new L.marker([points[i][1],points[i][2]])
                                    .bindPopup("<b>Location: "+points[i][0] + "</b><br>" + "<a href=http://gsd.spc.int/wacop/" + points[i][4].trim() + " target=_blank>See wave climate report</a>");
                        ocean.dsConf.ww3.overlay.addLayer(marker);
                    }
                    return false;
                  })

                  .fail(function( jqxhr, settings, exception ) {
                    fatal_error("Failed to load location points to show WACOP wave atlas report.");
                  });

                ocean.mapObj.addLayer(ocean.dsConf.ww3.overlay);

                if (map.hasLayer(map.intersecMarker)){
                    disableIntersecMarker();
                }
            }
        },
        onDeselect: function(){
            if (map.hasLayer(ocean.dsConf.ww3.overlay)){
                ocean.mapObj.removeLayer(ocean.dsConf.ww3.overlay);
            }
        },
        onVariableChange: function(){},
        onRegionChange: function() {}

    },
    tideforecast: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
            /*ocean.dsConf.tideforecast.overlay = new L.FeatureGroup();

            //Current year
            var year_0 = (new Date()).getFullYear();
            var year_1 = year_0 + 1;
            var year_2 = year_1 + 1;

            //Load the markers
            var base_pdf_url = "http://www.bom.gov.au/ntc/IDO59001/IDO59001_";
            var high_tide_content = ""
            var low_tide_content = ""

            points = data;

            for (var key in points){
                var point = points[key];

                var web_url =  "http://www.bom.gov.au/australia/tides/#!/offshore-" + point.short_name.trim();
                var pdf_url_0 =  base_pdf_url  + year_0 + "_" + point.station_number.trim() + ".pdf";
                var pdf_url_1 =  base_pdf_url  + year_1 + "_" + point.station_number.trim() + ".pdf";
                var pdf_url_2 =  base_pdf_url  + year_2 + "_" + point.station_number.trim() + ".pdf";

                if (point.high_tide_time && point.current_time){
                    var nextHighTide = point.high_tide_time - point.current_time;
                    var high_hour = Math.floor(nextHighTide/(60*60));
                    var high_min = Math.floor((nextHighTide % (60 * 60)) / 60);
                    var high_tide_content = "Next high tide in: <b>" + high_hour + "  hrs " + high_min + "  min ("+ point.high_tide_height + " m)</b><br>";
                }

                if (point.low_tide_time && point.current_time){
                    var nextLowTide = point.low_tide_time - point.current_time;
                    var low_hour = Math.floor(nextLowTide/(60*60));
                    var low_min = Math.floor((nextLowTide % (60 * 60)) / 60);
                    var low_tide_content =  "Next low tide in: <b>" + low_hour + "  hrs " + low_min + "  min (" + point.low_tide_height + " m)</b><br>";
                }

                var popup_content = "<h4>"+ key + "</h4>"
                       + high_tide_content
                       + low_tide_content
                       + "<br>Tide forecast reports:<br>"
                       + "<a href=" + pdf_url_0 + " target=_blank>" + year_0 + "</a>  "
                       + "<a href=" + pdf_url_1 + " target=_blank>" + year_1 + "</a>  "
                       + "<a href=" + pdf_url_2 + " target=_blank>" + year_2 + "</a>" + "<br><br>"
                       + "<a href=" + web_url + " target=_blank>Go to Tide Prediction website</a>";

                var marker = new L.marker(point.latlng).bindPopup(popup_content);
                ocean.dsConf.tideforecast.overlay.addLayer(marker);
            }

            ocean.mapObj.addLayer(ocean.dsConf.tideforecast.overlay);*/
        },
        onSelect: function(){
            resetMap();
            resetLegend();
            if (ocean.variable == 'tide'){
                ocean.dsConf.tideforecast.overlay = new L.FeatureGroup();

                //Current year
                var year_0 = (new Date()).getFullYear();
                var year_1 = year_0 + 1;

                var BASE_URL = "http://www.bom.gov.au/australia/tides/scripts/getNextTides.php?";
                var base_pdf_url = "http://www.bom.gov.au/ntc/IDO59001/IDO59001_";

                //Read file
                $.getScript("js/comp/tide_gauges_to_load.js")
                    .done(function( script, textStatus ) {
                        for (var i = 0; i < points.length; i++) {
                            var web_url =  "http://www.bom.gov.au/australia/tides/#!/offshore-" + points[i][4].trim();
                            var pdf_url_0 =  base_pdf_url  + year_0 + "_" + points[i][6].trim() + ".pdf";
                            var pdf_url_1 =  base_pdf_url  + year_1 + "_" + points[i][6].trim() + ".pdf";
                            var url = BASE_URL + "aac=" + points[i][6] + "&offset=false&tz=" + points[i][5];
                            var popup_content = "<h4 id='title'>"+ points[i][0] + "</h4>"
                                   + "<p id='website'><a href=" + web_url + " target=_blank>Go to Tide Prediction website</a></p>"
                                   + "<p id='url' style='display:none;'>" + url + "</p>"
                                   + "<p id='reports'>Tide forecast reports: " + "<a href=" + pdf_url_0 + " target=_blank>" + year_0 + "</a>  <a href=" + pdf_url_1 + " target=_blank>" + year_1 + "</a></p>";

                            //Load the markers
                            var marker = new L.marker([points[i][1],points[i][2]]).bindPopup(popup_content).on('popupopen', getTideInfo);
                            ocean.dsConf.tideforecast.overlay.addLayer(marker);
                        }

                        return false;
                    })

                    .fail(function( jqxhr, settings, exception ) {
                        fatal_error("Failed to load location points to show tide calendar report.");
                    });

                ocean.mapObj.addLayer(ocean.dsConf.tideforecast.overlay);

                if (map.hasLayer(map.intersecMarker)){
                    disableIntersecMarker();
                }
            }
        },
        onDeselect: function(){
            if (map.hasLayer(ocean.dsConf.tideforecast.overlay)){
                ocean.mapObj.removeLayer(ocean.dsConf.tideforecast.overlay);
            }
        },
        onVariableChange: function(){},
        onRegionChange: function() {}

    },
    msla: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function(){
            valid = true;
            return valid;
        },
        callback: function(data) {
            if (data.img != null && data.scale != null){
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
               // updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            enablePointClick();
        },
        onDeselect: function(){
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function() {
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    poamasla: {
        params: override(function (dataset) { return {
                'step' : slider.getStep()[0] - 1
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
    //                $.extend(ocean.dataset.params(), {'step', this.getStep()[0] - 1});
        //            $.extend(ocean.dataset.params(), {'step': this.getStep()[0] - 1});
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime);
                    $('.slider-hint').text('');
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                      //  updateMap(data.mapimg);
                        if (!hasResultOverlay()){
                            updateMapTiles(data.map, data.mapimg);
                        }
               ///         doPointClick();
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                     //   updateMap(data.mapimg);
                        updateMapTiles(data.map, data.mapimg);
                        doPointClick();
                    }
                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function() {
            updatePage();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:'',
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    poamassta: {
        params: override(function (dataset) { return {
                'step' : slider.getStep()[0] - 1
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime);
                    $('.slider-hint').text('');
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        if (data.contour) {
                            data.contour = data.contour.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                            data.normal = data.normal.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                            if (!hasResultOverlay()){
                                updateMapTilesSst(data.map, data.mapimg, data.contour, data.normal);
                            }
                        }
                        else {
                            // updateMap(data.mapimg);
                            if (!hasResultOverlay()){
                                updateMapTiles(data.map, data.mapimg);
                            }
                            //updateMapTiles(data.map, data.mapimg);
                        }
                    }

                    if (data.scale) {
                        data.scale = data.scale.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        setLegend(data.scale);
                    }
                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        if (data.contour) {
                            data.contour = data.contour.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                            data.normal = data.normal.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                            updateMapTilesSst(data.map, data.mapimg, data.contour, data.normal);
                        }
                        else {
                            // updateMap(data.mapimg);
                            updateMapTiles(data.map, data.mapimg);
                        }
                        doPointClick();
                    }

                    if (data.scale) {
                        data.scale = data.scale.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        setLegend(data.scale);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function() {
            updatePage();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:'',
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    currentforecast: {
        params: override(function (dataset) { return {
                'step' : slider.getStep()[0] - 1
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.map = data.map;
                this.mapimg = data.mapimg;
                this.overlayimg = data.arrow;
                this.downloadimg = data.img;

                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[Math.round(this.getStep()[0]) - 1].datetime  + 'UTC');//Math.round is to fix a problem found when getStep returns somthing like 30.000000000000004.
                    //display local time
                    var dt = forecast[this.getStep()[0] - 1].datetime
                    var local = getLocalTime(dt);
                    $('.slider-hint').text(local.toString());
                    if (data.mapimg) {
                        if (!hasResultOverlay()){
                             ocean.dataset.updateMapImg();
                        }
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        ocean.dataset.updateMapImg();
                        doPointClick();
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        onVariableChange: function() {
            updatePage();
        },
        updateMapImg: function() {
            mapimg = this.mapimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
            overlayimg = this.overlayimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
            if (!this.selectedRegion) {
                this.selectedRegion = ocean.area;
            }
            if (this.selectedRegion !== ocean.area) {
                mapimg = mapimg.replace('_' + this.selectedRegion, '_' + ocean.area);
                overlayimg = overlayimg.replace('_' + this.selectedRegion, '_' + ocean.area);
                this.mapimg = mapimg;
                this.overlayimg = overlayimg;
                this.selectedRegion = ocean.area;
            }
            updateMapTiles(this.map, mapimg, overlayimg);
           // bounds = $('#subregion option:selected').data('bounds');
           // if ($('#subregion option:selected').val() === 'pac') {
           //     bounds = null;
           // }
           // updateMap(mapimg, bounds);
        },
        onRegionChange: function() {
            this.updateDownloadImg();
            this.updateMapImg(this.mapimg);
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
             }
        },
        selectedRegion: ocean.area,
        mapimg: '',
        downloadimg:'',
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    sealevel: {
        params: override(function (dataset) { return {
            lat: $('#latitude').val(),
            lon: $('#longitude').val(),
            tidalGaugeId: $('#tgId').val()
        };}),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            if (ocean.plottype === "ts") {
                if (["rec", "alt"].indexOf(variable) != -1) {
                    valid = isLocationPointValid();
                    if (!valid){
                        text = location_missing_msg;
                    }
                }
                else if (ocean.variable === "gauge" && $('#tgId').val().trim() === "") {
                    text = "Please select a tide gauge from the map.";
                    valid = false;
                }
            }
            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid; 
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img) {
                appendOutput(data.img, null, null, null, data);
              //  updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
            }

            if (data.tidimg)
                appendOutput(data.tidimg, data.tidtxt, "Tide Gauge");

            if (data.altimg)
                appendOutput(data.altimg, data.alttxt, "Altimetry");

            if (data.recimg)
                appendOutput(data.recimg, data.rectxt, "Reconstruction");

            setLegend(data.scale);
        },
        selectTideGauge: function(){
            seaLevelModel.selectTideGuage(feature.properties.ID)
        },
        onSelect: function() {
            var seaLevelModel = new $.SeaLevelModel();
            if (ocean.variable != 'gauge') {
                enablePointClick();
                return;
            }
            $.when(
                seaLevelModel.getData()
            ).done(function(tideGauges) { 
                ocean.dsConf.sealevel.overlay = L.geoJson(tideGauges.features, {
                    style: function(feature) {
                        return {color: '#000'};
                    },
                    onEachFeature: function(feature, layer) {
                        layer.bindPopup('<b>' + feature.properties.Description + ' (' + feature.properties.ID + ')</b> <br/><p>' + 'Latitude: ' + feature.geometry.coordinates[1] + ' Longitude: ' + feature.geometry.coordinates[0] + '</p>');
                        layer.on('popupopen', function() {
                            $("#tidalgauge").val(feature.properties.Description);
                            $("#tgId").val(feature.properties.ID);
                        });
                        layer.on('popupclose', function() {
                            $("#tidalgauge").val('');
                            $("#tgId").val('');
                        });
                    },
                    filter: function(feature, layer) {
                        return feature.properties.Region == ocean.configProps.tidalGaugeRegions;
                    }
                }).addTo(map)
            }).fail(function() {
                fatal_error("Failed to load tide gauges.");
            });

//
 //                   $('#tidalgauge').val('');
  //                  $('#tgId').val('');
   //                 $('#latitude').val('');
    //                $('#longitude').val('');
        },
        onDeselect: function() {
//            var control;
            if (map.hasLayer(ocean.dsConf.sealevel.overlay)) {
                map.removeLayer(ocean.dsConf.sealevel.overlay);
            }
            resetLegend();
            disablePointClick();
//            var controls = map.getControlsByClass(
//                'OpenLayers.Control.SelectFeature');

//            for (control in controls) {
//                map.removeControl(controls[control]);
//                controls[control].deactivate();
//                controls[control].destroy();
//            }
        }, 
        onVariableChange: function(){
            resetMap();
            resetLegend();
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(0);
        }
    },
    coral: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
            updateInfo(data.dial, 'Alert level');

        },
        onSelect: function() {
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            updateInfo(null, '');
            disablePointClick();
        }, 
        onVariableChange: function(){
            resetMap();
            resetLegend();
            updateInfo(null, '');
        },
        onRegionChange: function() {
            resetMap();
            updateInfo(null, '');
        },
        formatValue: function(value) {
            return value.toFixed(0);
        }
    },
    chlorophyll: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }

        },
        onSelect: function() {
            if ($('#tunafishing').parent('.fishery').size() == 1) {
                showControls('tunafishing');
            }
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            if ($('#tunafishing').parent('.fishery').size() == 1) {
                hideControls('tunafishing');
            }
            disablePointClick();
        }, 
        onVariableChange: function(){
        },
        onRegionChange: function() {},
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    convergence: {
        params: override(function (dataset) { return {
        };}),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                //updateMap(data.mapimg);
                updateMapTiles(data.map, data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            showControls('tunafishing');
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            hideControls('tunafishing');
            disablePointClick();
        }, 
        onVariableChange: function(){
            updateDatasetForSST();
        },
        onRegionChange: function(){
            updateDatasetForSST();
        },
        formatValue: function(value) {
            return value.toFixed(2);
        }
    },
    mur: {
        params: override(function (dataset) { return {
        };}),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
               // updateMap(data.mapimg);
                setLegend(data.scale);
            }
            if (data.mapimg) {
                updateMapTiles(data.map, data.mapimg, data.front, 'front');


                //this.mapimg = data.mapimg;
                //ocean.dataset.updateMapImg();
            }
        },
        onSelect: function() {
            enablePointClick();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            disablePointClick();
        },
        updateMapImg: function() {
            bounds = $('#subregion option:selected').data('bounds');
            if ($('#subregion option:selected').val() === 'pac') {
                bounds = null;
            }
            updateMap(this.mapimg, bounds);
        },
        onVariableChange: function(){
            updateDatasetForSST();
        },
        onRegionChange: function(){
            resetMap();
            updateDatasetForSST();
        },
        formatValue: function(value) {
            return value.toFixed(2);
        }
    }

};

function appendOutput(image, dataURL, name, extras, data){
    var captionText = ""
    if (dataURL) {
        captionText = "<a class='download-data' href=" + dataURL+ " target='_blank'><span class='ui-icon ui-icon-arrowreturnthick-1-s'></span>Download Data</a>"
    }
    if (extras) {
        captionText = captionText + extras
    }
    //Check if the img is already in the gallery. If not, then add the img.
    var index = -1;
    if (fotorama.data){
        for (var i=0; i<fotorama.data.length; i++){
            if (fotorama.data[i].img == image){
                index = i;
                i = fotorama.data.length;
            }
        }
    }

    if (index == -1){
        fotorama.push({img: image, caption: captionText});
    }

    if (fotorama.size > 20) {//TODO extract 20 to the config
        fotorama.shift();
    }

    if (index == -1){
        fotorama.show(fotorama.size - 1);
    } else {
        fotorama.show(index);
    }

    if (name) {
        $('<h2>', {
            text: name
        }).appendTo(captionText);
    }

    if (data) {
//        updateMap(data);
    }
}

/**
 * Pad number with leading zeros
 * https://gist.github.com/aemkei/1180489
 */
function pad(a,b){
    return([1e15]+a).slice(-b)
}

function updateInfo(image, altText){
    if (image != null) {
        $('#additionalInfoDiv').empty().append($('<img>', {src: image, alt: altText}));
    }
    else {
        $('#additionalInfoDiv').empty();
    }
}


/**
 * Opens the download image link in a new window for the datasets having slider option.
 */
function openDownloadImageLink(){
    if (ocean.sliderdownloadlink != ""){
        appendOutput(ocean.sliderdownloadlink);
    }
}


/**
 * Merge the Reynolds daily sst product in fisheries with the MUR.
 * http://tuscany/redmine/issues/729
 */

function updateDatasetForSST(){
    if (getValue('region') == 'pac'){
        addOption('dataset', 'convergence', 'Reynolds');
        ocean.variable = 'mean';
    } else { //for subregions
        addOption('dataset', 'mur', 'High Resolution SST & Fronts');
        ocean.variable = 'mursst';
    }

    //Updates the available date.
    updateDatepicker();
}

//gets local time
function getLocalTime(dt){
    //Example datetime string
    //"26-01-2015 12:00"
    local = new Date(dt.slice(6,10),dt.slice(3,5)-1,dt.slice(0,2),dt.slice(11,13),dt.slice(14));
    var hourOffset = local.getTimezoneOffset() / 60;
    local.setHours(local.getHours() - hourOffset);
    return local;
}

function isLocationPointValid(){
    var valid = true;
    if (($('#latitude').val().trim() === "") || ($('#longitude').val().trim() === "")){
        valid = false;
    }

    return valid;
}

function getTideInfo(e) {
    $('#loading-dialog').dialog('open');

    var popup = e.target.getPopup();

    //Retrieving url from the cpopup content
    var children = popup._contentNode.children;
    var title = '';
    var website = '';
    var url = '';
    var reports = '';

    for(var i=0; i < children.length; i++){
        if (children[i].id == 'title'){
            title = children[i].innerHTML.trim();
        } else if (children[i].id == 'website'){
            website = children[i].innerHTML.trim();
        } else if (children[i].id == 'url'){
            url = children[i].textContent.trim();
        } else if (children[i].id == 'reports'){
            reports = children[i].innerHTML.trim();
        }
    }

    // As the machines inside DMZ are not accessible from the outside, so we are taking advantage of Yahoo Query Language (YQL) to get the json response from the cross domain request.
    // https://developer.yahoo.com/yql/

    //We are not using the data.current_time as its corresponding ajax response is inconsistant. Instead we use the system time. Also we are adding the random current_time_ms in the url to force YQL not to get response from cache. 
    var d = new Date();
    var current_time_ms = d.getTime();
    var current_time = current_time_ms/1000;

    request_url = 'http://query.yahooapis.com/v1/public/yql?q=' + encodeURIComponent('select * from html where url="' + url + "&rnd=" + current_time_ms + '"') + '&format=json';

    if (request_url != ''){
        $.ajax({
            type: 'GET',
            url: request_url,
            dataType:"text",
            success: function(text) {
               if ($.parseJSON(text).query.results){
                    data = $.parseJSON($.parseJSON(text).query.results.body).results;
               }

               var new_content = '';
               var high_tide_content = '';
               var low_tide_content = '';

               if (data.next_high.time && (data.next_high.time - current_time > 0)){
                    var nextHighTide = data.next_high.time - current_time;
                    var high_hour = Math.floor(nextHighTide/(60*60));
                    var high_min = Math.floor((nextHighTide % (60 * 60)) / 60);
                    high_tide_content = "<p id ='tide'>Next high tide in: <b>" + high_hour + "  hrs " + high_min + "  min ("+ data.next_high.height + " m)</b><br/>";
               }

               if (data.next_low.time && (data.next_low.time - current_time > 0)){
                    var nextLowTide = data.next_low.time - current_time;
                    var low_hour = Math.floor(nextLowTide/(60*60));
                    var low_min = Math.floor((nextLowTide % (60 * 60)) / 60);
                    low_tide_content =  "Next low tide in: <b>" + low_hour + "  hrs " + low_min + "  min (" + data.next_low.height + " m)</b></p>";
               }

               if ((high_tide_content != '') && (low_tide_content != '')){
                    new_content = "<h4 id='title'>"+ title + "</h4>"
                                   + "<p id='website'>" + website + "</p>"
                                   + "<p id='url' style='display:none;'>" + url + "</p>"
                                   + "<p id='reports'>" + reports + "</p>"
                                   + high_tide_content + low_tide_content;

                    popup.setContent(new_content);
               }
            },
            error: function(xhr, status, error) {
               console.log('error');
               console.log(xhr);
            },
            complete: function(xhr, status) {
                $('#loading-dialog').dialog('close');
            }
        });
    }
}
