FROM ubuntu

MAINTAINER sachindras@spc.int

RUN DEBIAN_FRONTEND=noninteractive apt-get -y update

RUN apt-get -y install python-matplotlib python-matplotlib-data python-mpltoolkits.basemap python-mpltoolkits.basemap-data python-mapscript cgi-mapserver  python-matplotlib-venn libhdf4-0 netcdf-bin nco python-netcdf4 python-numpy python-scipy gdal-bin libgdal1i python-gdal libgeos-3.5.0 libgeos-c1v5 hdf5-tools hdf5-tools hdf5-tools libhdf5-10 libhdf5-cpp-11 python-h5py libnetcdf-c++4 libnetcdf-c++4-1 libnetcdf11 proj-bin proj-data python-pyproj libgeotiff-epsg python-pip python-setuptools python-dateutil git pngcrush emacs apache2 python-mplexporter lftp wget

RUN apt-get -y clean

RUN mkdir -p /opt/data && mkdir -p /opt/ocean-portal

EXPOSE 80

# Set Apache environment variables (can be changed on docker run with -e)
#ENV APACHE_RUN_USER www-data
#ENV APACHE_RUN_GROUP www-data
#ENV APACHE_LOG_DIR /var/log/apache2
#ENV APACHE_PID_FILE /var/run/apache2.pid
#ENV APACHE_RUN_DIR /var/run/apache2
#ENV APACHE_LOCK_DIR /var/lock/apache2
#ENV APACHE_SERVERADMIN admin@localhost
#ENV APACHE_SERVERNAME localhost
#ENV APACHE_SERVERALIAS docker.localhost
#ENV APACHE_DOCUMENTROOT /var/www

ADD ./index.html /var/www/html/
RUN a2dissite 000-default
RUN a2enmod cgi
ADD ./ocean-portal.conf /etc/apache2/sites-available/
RUN ln -s /etc/apache2/sites-available/ocean-portal.conf /etc/apache2/sites-enabled/
RUN a2ensite ocean-portal

#CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
CMD ["apachectl", "-D", "FOREGROUND"]
