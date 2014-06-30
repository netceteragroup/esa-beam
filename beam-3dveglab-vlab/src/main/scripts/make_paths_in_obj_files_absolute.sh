#!/bin/bash

LIBRAT_SCENES="${HOME}/.beam/beam-vlab/auxdata/librat_scenes/"

if which parallel
then
    find "$LIBRAT_SCENES" -regex ".*\\.\\(obj\\(\\.crown\\)?\\|dem\\)"         \
         -exec parallel --progress --eta                                       \
         ./make_paths_in_obj_file_absolute.sh ::: {} +
else
    find "$LIBRAT_SCENES" -regex ".*\\.\\(obj\\(\\.crown\\)?\\|dem\\)"         \
         -exec ./make_paths_in_obj_file_absolute.sh {} \;
fi
