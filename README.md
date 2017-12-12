Pacific Ocean Portal
====================

Dockerised on Ubuntu 16.04, Mapserver 7.0.x, System-wide Python Libraries and Dependencies

1. create `data` directy
2. checkout project next to `data` directory

Setup: In cloned project directory -

1. docker-compose up
2. Open http://servername in browser

Developpement :

To have changes applied live (for developement), uncomment `# - .:/ocean-portal` in `docker-compose.yml` and run `docker-compose up --build`.

---
Geoinformatics Section, Geoscience Division, Pacific Community (SPC) | 
ict4dev@spc.int
