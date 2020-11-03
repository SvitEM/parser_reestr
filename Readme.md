GET /

{"hello from parser": true}

GET /parse
params {id, type, bday}

POST /parse-multy
params {[{id, bday}], type}