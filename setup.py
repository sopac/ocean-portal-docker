#/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

NAME                = 'map-portal'
DESCRIPTION         = 'Map Portal'
LONG_DESCRIPTION    = """\
COMP Group Climate Portal
"""
AUTHOR              = 'COMP'
AUTHOR_EMAIL        = 'COSPPac_COMP_Unit@bom.gov.au'
URL                 = 'http://tuscany.bom.gov.au/wiki/index.php/Map_Portal'

rpm_deps = [
    'basemap >= 1.1.7',
    'mapserver-python >= 6.0.1',
    'matplotlib >= 1.1.0',
    'netCDF4 >= 0.9.7',
    'numpy >= 1.6.1',
    'scipy >= 0.9.0',
]

src = [
    'map.py',
    'portal.py',
    'regions.py',
    'logs.py',
]

packages = [
    'ocean',
    # core
    'ocean.config',
    'ocean.netcdf',
    'ocean.util',
    'ocean.plotter',
    'ocean.processing',
    # dataset
    'ocean.datasets',
    'ocean.datasets.bran',
    'ocean.datasets.ersst',
    'ocean.datasets.sealevel',
    'ocean.datasets.reynolds',
    'ocean.datasets.ww3',
    'ocean.datasets.ww3forecast',
    'ocean.datasets.coral',
    'ocean.datasets.chlorophyll',
    'ocean.datasets.poamasla',
    'ocean.datasets.poamassta',
    'ocean.datasets.currentforecast',
    'ocean.datasets.convergence',
    'ocean.datasets.msla',
    'ocean.datasets.mur',
    'ocean.datasets.tideforecast'
]

scripts = [
    'replicate-portal-data',
    'cleanup-raster-cache',
    'update-data'
]

# run generate-manifest.py after editing these sections
backend_resources = [
    'maps/bathymetry.map',
    'maps/mean.map',
    'maps/mean_sub.map',
    'maps/anom.map',
    'maps/dec.map',
    'maps/trend.map',
    'maps/hs.map',
    'maps/chlo.map',
    'maps/coral_daily.map',
    'maps/coral_outlook.map',
    'maps/wav.map',
    'maps/wnd.map',
    'maps/grey.map',
    'maps/poamasla.map',
    'maps/current.map',
    'maps/mur.map',
    'maps/contour.map',
    'maps/normal.map',
    'maps/salt.map',
    'maps/uv.map',
    'maps/front.map',
    'maps/height.map',
    'fonts/fonts.list',
    'fonts/DejaVuSans.ttf',
]

map_layer_extensions = ['dbf', 'prj', 'shp', 'shx' ]
map_layers = [
    'bathymetry_0',
    'bathymetry_200',
    'bathymetry_1000',
    'bathymetry_2000',
    'bathymetry_3000',
    'bathymetry_4000',
    'bathymetry_5000',
    'bathymetry_6000',
    'bathymetry_7000',
    'bathymetry_8000',
    'bathymetry_9000',
    'bathymetry_10000',
    'ocean',
    'pacific_islands_capitals',
    'southern_pac',
    'northern_pac',
    'land',
    'COSPPac_EEZs',
    'ReefLocations',
    'CRW_Outlines',
    'MP_FINAL',
    'CRW_Outlook_EEZ'
]

BASE_PATH = 'share/portal'
html = [
    'ocean.html',
    'app.html'
]

script_substitutions = {
    # development version, compressed version
    'jquery.js': ('jquery-1.11.3.js', 'jquery-1.11.3.min.js'),
    'jquery-ui.js': ('jquery-ui-1.9.2.custom/js/jquery-ui-1.9.2.custom.js',
                     'jquery-ui-1.9.2.custom/js/jquery-ui-1.9.2.custom.min.js'),
    'jquery-ui.css': ('jquery-ui-1.9.2.custom/css/smoothness/jquery-ui-1.9.2.custom.css',
                      'jquery-ui-1.9.2.custom/css/smoothness/jquery-ui-1.9.2.custom.min.css'),
    'OpenLayers.js': ('OpenLayers.js', 'OpenLayers.min.js'),
}

web_files = [
    'css/comp/controlPanel.css',
    'css/comp/compmap.css',
    'css/comp/controlvars.css',
    'css/comp/jumbotron.css',
    'css/comp/dragdealer.css',
    'js/comp/controlPanel.js',
    'js/comp/compmap.js',
    'js/comp/dsConf.js',
    'js/comp/app.js',
    'js/comp/dragdealer.js',
    'js/comp/Ocean.js',
    'js/comp/data_points_to_load.js',
    'js/comp/tide_gauges_to_load.js'
]

data = [
    'config/comp/datasets.json',
    'config/comp/vargroups.json',
    'config/comp/portals.json',
    'config/comp/app.json',
    'config/comp/tidegauges.geojson',
    'images/search.gif',
    'images/calendar-blue.gif',
    'images/blank.png',
    'images/loading.gif',
    'images/notavail.png',
    'images/climate.jpg',
    'images/bom_logo.gif',
    'images/bathymetry_ver.png',
    'images/email.png',
    'images/climate.png',
    'images/coral.png',
    'images/fishing.png',
    'images/sealevel.png',
    'images/shipping.png',
    'images/surfer.png',
    'images/daily_0.png',
    'images/daily_1.png',
    'images/daily_2.png',
    'images/daily_3.png',
    'images/daily_4.png',
    'images/outlook_0.png',
    'images/outlook_1.png',
    'images/outlook_2.png',
    'images/outlook_3.png',
    'images/outlook_4.png',
    'help/about_BRAN.pdf',
    'help/about_sealevel.pdf',
    'help/about_ww3forecasts.pdf',
    'help/about_ww3climate.pdf',
    'help/about_chlorophyll.pdf',
    'help/about_coralbleaching.pdf',
    'help/about_currents.pdf',
    'help/about_OceanTemperature.pdf',
    'help/about_POAMA_Sea_Level.pdf',
    'help/about_POAMA_SST.pdf',
    'help/Beverly_11_Remote_sensing_guide.pdf',
    'help/about_AVISO_Sea_Level.pdf',
    'help/about_MUR_Fronts.pdf'
]

# CODE BEGINS
import os.path

backend_resources += [ os.path.join('maps', 'layers', '%s.%s' % (l, ext))
                        for l in map_layers
                        for ext in map_layer_extensions ]

if __name__ == '__main__':
    from distutils.core import setup
    from distutils.command.bdist_rpm import bdist_rpm

    from localdistutils.dist import PortalDist
    from localdistutils.build import build
    from localdistutils.build_py import build_py
    from localdistutils.build_web import build_web
    from localdistutils.install import install
    from localdistutils.install_web import install_web
    from localdistutils import util

    import itertools

    # add Requires: for RPM
    _original_make_spec_file = bdist_rpm._make_spec_file
    def _make_spec_file(*args):
        spec = _original_make_spec_file(*args)
        spec.insert(spec.index('%description') - 1,
                    'Requires: %s' % ', '.join(rpm_deps))
        return spec
    bdist_rpm._make_spec_file = _make_spec_file

    data_files = \
        [ ('/var/www/cgi-bin/portal', [ os.path.join('src', s) for s in src ]) ] + \
        [ (os.path.join(BASE_PATH, d), list(f))
            for d, f in itertools.groupby(data, lambda e: os.path.dirname(e)) ]

    setup(name=NAME,
          version=util.get_version(),
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,

          packages=packages,
          package_data={
              'ocean': [ os.path.join('resource', r)
                         for r in backend_resources ],
          },
          scripts=[ os.path.join('src', s) for s in scripts ],
          data_files = data_files,

          # FIXME: BASE_PATH here is ignored because I'm lazy, BASE_PATH from
          # web_files is used
          html_files = (BASE_PATH,
                        [ os.path.join('html', h) for h in html ],
                        script_substitutions),
          web_files = (BASE_PATH, web_files),

          # extend distutils
          distclass=PortalDist,
          cmdclass={
              'build': build,
              'build_py': build_py,
              'build_web': build_web,
              'install': install,
              'install_web': install_web,
          },
         )
